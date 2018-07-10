import math

import GroupBlockManage

class FileManager:
    def __init__(self):
        self.empty_block_manager = GroupBlockManage.EmptyBlockManager()
        self.inode_manager = iNodeManager()
        self.root_dir = DirFile("", self, 0)

    def create_file(self, type_, file_name, work_dir, group_id):
        if work_dir.get_file(file_name) is not None:
            return -1
        if type_ == "plain":
            file = PlainFile(file_name, self, group_id)
            if file.inode_id == -1:
                return -1
            work_dir.add_file(file)
            return file
        if type_ == "dir":
            file = DirFile(file_name, self, group_id)
            if file.inode_id == -1:
                return -1
            work_dir.add_file(file)
            return file

    def search_file(self, path, work_dir):
        """
        根据路径寻找文件  目标可以是普通文件 或者目录文件
        :return:
        """
        if path.startswith("/"):
            start_dir = self.root_dir
        else:
            start_dir = work_dir
        path = path.split("/")
        search_route = []
        curr_dir = start_dir
        next_dir = curr_dir  # 如果传入路径为空的话 返回起点目录

        for each in range(len(path)):
            dir_name = path[each]
            if dir_name == "":
                continue
            search_route.append(curr_dir)
            next_dir = curr_dir.get_file(dir_name)  # 获取下一路径的文件
            if next_dir is not None:  # 当文件不为空时 继续步进
                if next_dir.get_type_name() == "DirFile" and each != len(path) - 1:
                    # 文件为目录类型  且不为最后一个 继续步进
                    curr_dir = next_dir
                if each == len(path) - 1:
                    break  # 文件路径以步进至最后一个token 且搜索得到的文件不为空
                    # 也不为目录文件  说明找到了正确文件返回
            else:
                return -1, -1
        return next_dir, search_route

    def open_file(self, file_name, work_dir, group_id):
        file = work_dir.get_file(file_name)
        if file is not None:
            if file.get_type_name() != "DirFile":
                return file
            else:
                return None
        else:
            return self.create_file("plain", file_name, work_dir, group_id)

    def free_block(self, block):
        return self.empty_block_manager.free_block(block)

    def alloc_block(self):
        return self.empty_block_manager.alloc_block()

    def acquire_inode(self):
        return self.inode_manager.create_inode()

    def free_inode(self, inode):
        self.inode_manager.recycle_inode(inode)

    @staticmethod
    def remove_file(file_name, work_dir):
        target_file = work_dir.get_file(file_name)
        if target_file is None:
            return -1
        FileManager.remove_file_walker(target_file, work_dir)
        return 0

    @staticmethod
    def remove_file_walker(target_file, curr_dir):
        """
        简单文件则直接删除
        如果删除的是个目录 以BFS方式级联删除其index的文件
        """
        file_list = [target_file]
        while len(file_list) != 0:
            target = file_list[0]
            file_list = file_list[1:]
            if target.get_type_name() == "PlainFile":
                curr_dir.remove_file(target)
                target.delete()
            if target.get_type_name() == "DirFile":
                file_list.extend(target.dir_dict.values())
                target.dir_dict.clear()
                curr_dir.remove_file(target)
                target.delete()


class iNodeManager:
    def __init__(self):
        self.available_inode = list(range(128))
        self.using_inode_list = {}
        self.inode_cnt = 0

    def create_inode(self):
        # acquire this inode address
        if len(self.available_inode) == 0:
            return -1
        inode = self.available_inode.pop()
        self.using_inode_list[inode] = 0
        return inode

    def recycle_inode(self, inode):
        self.using_inode_list[inode] = None


class File:
    """
    UNIX 核心概念 一切皆文件
    """
    def __init__(self, file_name, file_manager, group_id):
        self.file_name = file_name
        self.user = ""
        self.group_id = group_id
        self.file_manager = file_manager

        # iNode
        self.inode_id = self.file_manager.acquire_inode()
        self.block_dict = []
        self.block_dict.append(file_manager.alloc_block())
        self.file_length = 0

    def set_property(self, group_id):
        self.group_id = group_id

    def get_type_name(self):
        return self.__class__.__name__

    def delete(self):
        for each in self.block_dict:
            self.file_manager.free_block(each)
        self.file_manager.free_inode(self.inode_id)

    def __str__(self):
        res = "%-10s%-12s%-6s%-9s%s" % \
              (self.file_name, self.get_type_name(), self.group_id, self.inode_id, self.block_dict)
        return res


class PlainFile(File):
    def __init__(self, file_name, file_manger, group_id):
        File.__init__(self, file_name, file_manger, group_id)
        self.content = ""

    def read(self):
        return self.content

    def write(self, new_content):
        self.content = new_content
        self.update_length()

    def update_length(self):
        length = self.content.__len__()
        length /= 8
        length = int(math.ceil(length))
        update_len = length - self.file_length
        self.file_length = length
        if update_len > 0:
            for i in range(update_len):
                self.block_dict.append(self.file_manager.alloc_block())
        elif update_len < 0:
            for i in range(abs(update_len)):
                self.file_manager.free_block(self.block_dict.pop())


class DirFile(File):
    def __init__(self, dir_name, file_manager, group_id):
        File.__init__(self, dir_name, file_manager, group_id)
        self.dir_dict = {}

    def add_file(self, file):
        if self.dir_dict.get(file.file_name) is not None:
            return -1
        else:
            self.dir_dict[file.file_name] = file
            self.update_length()
            return 0

    def remove_file(self, file):
        if self.dir_dict.get(file.file_name) is None:
            return -1
        else:
            self.dir_dict.pop(file.file_name)
            self.update_length()
            return 0

    def get_file(self, file_name):
        return self.dir_dict.get(file_name)

    def update_length(self):
        length = len(self.dir_dict.keys())
        length = int(math.ceil(length))
        update_len = length - self.file_length
        self.file_length = length
        if update_len > 0:
            for i in range(update_len):
                self.block_dict.append(self.file_manager.alloc_block())
        elif update_len < 0:
            for i in range(abs(update_len)):
                self.file_manager.free_block(self.block_dict.pop())

    def as_text(self):
        res = "DirFile %s contains: \n" % self.file_name
        for each in self.dir_dict.values():
            res += str(each) + "\n"
        return res
