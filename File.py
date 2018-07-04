import GroupBlockManage
import math



class FileManager:
    def __init__(self):
        self.empty_block_manager = GroupBlockManage.EmptyBlockManager()
        self.root_dir = DirFile("", self)

    def create_file(self, type_, file_name, work_dir):
        if work_dir.get_file(file_name) is not None:
            return -1
        if type_ == "plain":
            file = PlainFile(file_name, self)
            work_dir.add_file(file)
            return file
        if type_ == "dir":
            file = DirFile(file_name, self)
            work_dir.add_file(file)
            return file

    @staticmethod
    def remove_file_walker(target_file, curr_dir):
        """
        简单文件则直接删除
        如果删除的是个目录 以BFS方式级联删除其index的文件
        """
        file_list = [target_file]
        while len(file_list) != 0:
            target = file_list.pop()
            if target.get_type_name() == "PlainFile":
                curr_dir.remove_file(target)
                target.delete()
            if target.get_type_name() == "DirFile":
                file_list.extend(target.dir_dict.values())
                target.dir_dict.clear()
                curr_dir.remove_file(target)
                target.delete()


    @staticmethod
    def remove_file(file_name, work_dir):
        target_file = work_dir.get_file(file_name)
        FileManager.remove_file_walker(target_file, work_dir)

    def open_file(self,file_name, work_dir):
        file = work_dir.get_file(file_name)
        if file is not None:
            if file.get_type_name() != "DirFile":
                return file
            else:
                return None
        else:
            return self.create_file("plain", file_name, work_dir)


    def free_block(self, block):
        return self.empty_block_manager.free_block(block)

    def alloc_block(self):
        return self.empty_block_manager.alloc_block()



class File:
    """
    UNIX 核心概念 一切皆文件
    """
    def __init__(self, file_name, file_manager):
        self.file_name = file_name
        self.block_dict = []
        self.block_dict.append(file_manager.alloc_block())
        self.file_length = 0
        self.file_manager = file_manager
        self.user = ""

    def set_property(self, username):
        self.user = username

    def get_type_name(self):
        return self.__class__.__name__

    def delete(self):
        for each in self.block_dict:
            self.file_manager.free_block(each)


class PlainFile(File):
    def __init__(self, file_name, file_manger):
        File.__init__(self, file_name, file_manger)
        self.content = ""

    def get_content(self):
        return self.content

    def set_content(self, new_content):
        self.content = new_content
        self.update_length()


    def update_length(self):
        length = self.content.__len__()
        length /= 8
        length = int(math.ceil(length))
        update_len =  length - self.file_length
        self.file_length = length
        if update_len > 0:
            for i in range(update_len):
                self.block_dict.append(self.file_manager.alloc_block())
        elif update_len < 0:
            for i in range(abs(update_len)):
                self.file_manager.free_block(self.block_dict.pop())


class DirFile(File):
    def __init__(self, dir_name, file_manager):
        File.__init__(self, dir_name, file_manager)
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
        update_len =  length - self.file_length
        self.file_length = length
        if update_len > 0:
            for i in range(update_len):
                self.block_dict.append(self.file_manager.alloc_block())
        elif update_len < 0:
            for i in range(abs(update_len)):
                self.file_manager.free_block(self.block_dict.pop())


