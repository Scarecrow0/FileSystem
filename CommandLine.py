import File


class CLI:


    def __init__(self):
        self.file_manager = File.FileManager()
        self.work_dir = self.file_manager.root_dir
        self.dir_route = []


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
        path = arg[0][0]
        if path == "..":
            if self.work_dir != self.file_manager.root_dir:
                self.work_dir = self.dir_route.pop()
                self.pwd()
                return

        if path.startswith("/"):
            start_dir = self.file_manager.root_dir
        else:
            start_dir = self.work_dir
        path = path.split("/")
        tmp_route = []
        curr_dir = start_dir
        next_dir = None

        for each in range(len(path)):
            dir_name = path[each]
            if dir_name != "":
                next_dir = curr_dir.get_file(dir_name)
                if next_dir is not None:
                    if next_dir.get_type_name() == "DirFile":
                        tmp_route.append(curr_dir)
                        curr_dir = next_dir
                else:
                    print("cant find dir")

        self.work_dir = next_dir
        if start_dir == self.file_manager.root_dir:
            self.dir_route = tmp_route
        else:
            self.dir_route.extend(tmp_route)

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
        pass

    def rm(self, *arg):
        pass


    def pwd(self, *arg):
        print(self.get_wd())

    def get_wd(self):
        res = ""
        for each in self.dir_route:
            res += each.file_name + "/"
        res += self.work_dir.file_name + "/"
        return res

    cmd_dict = {
        "pwd": pwd,
        "cd" : cd,
        "mkdir": mkdir,
        "rm": rm,
        "edit": edit,
        "ls": ls

    }