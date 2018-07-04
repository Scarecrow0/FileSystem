import File

"""
对于工作目录来说 ，就如同是打开一个个目录文件
"""


class CLI:
    def __init__(self):
        self.file_manager = File.FileManager()
        self.work_dir = self.file_manager.root_dir
        self.dir_route = []

    """
    命令行执行的核心循环，在该循环中进行各种命令的交互
    """
    def main_loop(self):
        while True:
            print("$ >", end="")
            cmd = input()
            cmd = cmd.split(" ")
            func = CLI.cmd_dict.get(cmd[0])
            if func is not None:
                func(self, cmd[1:])
            else:
                print("no such cmd")


    def cd(self, *arg):
        try:
            path = arg[0][0]
        except IndexError:
            print("no enough args")
            return
        if path == "..":
            if self.work_dir != self.file_manager.root_dir:
                self.work_dir = self.dir_route.pop()
                self.pwd()
                return

        target_dir, search_route = self.search_file(path)

        if target_dir == -1:
            print("can't not find file ")
            return
        if len(search_route) == 0: # 如果搜索路径路程为空 说明距离目标只有一步，
            self.dir_route.append(self.work_dir)  # 在进行更换wd时，将原工作目录其放入路径中
        self.work_dir = target_dir

        if path.startswith("/"):
            self.dir_route = search_route
        else:
            self.dir_route.extend(search_route)

        self.pwd()


    def mkdir(self, *arg):
        try:
            dir_name = arg[0][0]
        except IndexError:
            print("no enough args")
            return
        if self.file_manager.create_file("dir", dir_name, self.work_dir) == -1:
            print("file has existed")
        else:
            self.ls()


    def ls(self, *args):
        print("in curr dir:")
        for each in self.work_dir.dir_dict.values():
            print("%-10s%-15s%s" % (each.file_name, each.get_type_name(), str(each.block_dict)))


    def edit(self, *arg):
        try:
            path = arg[0][0]
        except IndexError:
            print("no enough args")
            return
        path = path.split("/")
        file_name = path[-1]
        tmp_path = ""
        for each in range(len(path)-1):
            tmp_path  +=  path[each] + "/"
        path = tmp_path
        # 去掉目标文件得到目标文件的目录地址  先找到目标文件的目录位置 作为临时工作目录
        # 随后在这个工作目录 对目标文件进行打开操作
        target_file, search_route = self.search_file(path)
        if target_file == -1:
            print("can't find file")
            return

        work_dir = target_file

        file = self.file_manager.open_file(file_name, work_dir)
        if file is None:
            print("can only edit plain text file")
            return
        print("file content:\n%s" % file.content)
        print("please input things and end up with $ in single line")
        content = ""
        while True:
            line = input()
            if line == "$":
                file.set_content(content+"\n")
                break
            else:
                content += line


    def rm(self, *arg):
        try:
            path = arg[0][0]
        except IndexError:
            print("no enough args")
            return

        path = path.split("/")

        file_name = path[-1]
        tmp_path = ""
        for each in range(len(path) - 1):
            tmp_path += path[each] + "/"
        path = tmp_path
        # 去掉目标文件得到目标文件的目录地址  先找到目标文件的目录位置 作为临时工作目录
        # 随后在这个工作目录 对目标文件进行打开操作
        target_file, search_route = self.search_file(path)
        if target_file == -1:
            print("can't find file")
            return
        work_dir = target_file

        if self.file_manager.remove_file(file_name, work_dir) == -1:
            print("delete file %s failed" % target_file)
        else:
            print("delete file %s ok" % target_file)


    def pwd(self, *arg):
        print(self.get_wd())

    def show_blocks(self, *args):
        print(self.file_manager.empty_block_manager.__str__())

    def get_wd(self):
        res = ""
        for each in self.dir_route:
            res += each.file_name + "/"
        res += self.work_dir.file_name + "/"
        return res

    def search_file(self, path):
        """
        根据路径寻找文件  目标可以是普通文件 或者目录文件
        :param path:
        :return:
        """
        if path.startswith("/"):
            start_dir = self.file_manager.root_dir
        else:
            start_dir = self.work_dir
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
            if next_dir is not None:    # 当文件不为空时 继续步进
                if next_dir.get_type_name() == "DirFile" and each != len(path) -1 :
                    # 文件为目录类型  且不为最后一个 继续步进
                    curr_dir = next_dir
                if each == len(path)-1:
                    break  # 文件路径以步进至最后一个token 且搜索得到的文件不为空
                           # 也不为目录文件  说明找到了正确文件返回
            else:
                return  -1, -1
        return next_dir, search_route




    cmd_dict = {
        "pwd": pwd,
        "cd" : cd,
        "mkdir": mkdir,
        "rm": rm,
        "edit": edit,
        "ls": ls,
        "shblk": show_blocks

    }