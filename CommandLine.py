import os
import pickle
import time
import subprocess

import File
import UserDB

"""
对于工作目录来说 ，就如同是打开一个个目录文件
"""

# todo 展示文件树


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class CLI:
    def __init__(self):
        self.file_manager = File.FileManager()
        self.user_manager = UserDB.UserManager()
        self.curr_user = ''
        for root, dirs, files in os.walk("."):
            for file_ in files:
                if file_.startswith('load'):
                    print("find exist file archive, use it? y/n")
                    ans = input()
                    ans = ans.lower()
                    if ans == 'y':
                        file_ = open(file_, "r+b")
                        self.file_manager = pickle.load(file_)
                        self.user_manager.load_archive_exist()
                        file_.close()
                    else:
                        print("create new file")

        self.work_dir = self.file_manager.root_dir
        self.dir_route = []

    """
    命令行执行的核心循环，在该循环中进行各种命令的交互
    """
    def main_loop(self):
        if not self.user_check_in():
            return

        while True:
            print("\033[1;32m %s @%s\033[0m\033[1;34m $ >\033[0m" % (get_time(), self.curr_user), end="")
            cmd_raw = input()
            if cmd_raw == "exit":
                file_ = open("load", "w+b")
                pickle.dump(self.file_manager, file_)
                file_.close()
                self.user_manager.save_archive()
                print("file system has been saved ")
                return
            cmd = cmd_raw.split(" ")
            func = CLI.cmd_dict.get(cmd[0])
            if func is not None:
                func(self, *cmd[1:])
                self.user_manager.update_history(self.curr_user, cmd_raw, get_time())
            else:
                print("\033[1;31m no such cmd\033[0m")


    def cd(self, *arg):
        try:
            path = arg[0]
        except IndexError:
            print("\033[1;31m no enough args\033[0m")
            return
        while path.startswith(".."):
            if self.work_dir != self.file_manager.root_dir:
                self.work_dir = self.dir_route.pop()
                path = path[3:]
        if path == "":
            self.pwd()
            return

        target_dir, search_route = self.file_manager.search_file(path, self.work_dir)

        if target_dir == -1:
            print("\033[1;31m can't not find file \033[0m")
            return
        if self.user_manager.check_property(self.curr_user, target_dir.group_id) != 0:
            print("\033[1;31m can't not access to file , have not enough auth \033[0m")
            return
        if target_dir.get_type_name() != "DirFile":
            print("\033[1;31m can't open non DirFile \033[0m")
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
            path = arg[0]
        except IndexError:
            print("\033[1;31m no enough args\033[0m")
            return
        dir_name, belong_dir, search_path = self.search_file(path)
        if belong_dir == -1:
            print("\033[31m target dir is not existed\033[0m")
            return

        if self.create_dir_file(belong_dir, dir_name) == -1:
            print("\033[31m file has existed \033[0m")
        else:
            self.tree()


    def ls(self):
        print("in curr dir:")
        res = "%-10s%-12s%-6s%-9s%s" % \
              ("file_name", "file_type", "group", "inode_id", "occupied_block")
        print(res)
        for each in self.work_dir.dir_dict.values():
            print(str(each))
       # print("\033[1;33m in curr dir: \033[0m")
        #for each in self.work_dir.dir_dict.values():
        #    print(" "+str(each))

    def less(self, *args):
        try:
            path = args[0]
        except IndexError:
            print("\033[1;31m no enough args \033[0m ")
            return
        file_name, work_dir, search_path = self.search_file(path)
        if work_dir == -1:
            print("\033[1;31m can't find file \033[0m")
            return

        target_file, search_path = self.file_manager.search_file(file_name, work_dir)

        if target_file == -1:
            print("\033[1;31m can't find file\033[0m")
            return

        if target_file.get_type_name() == "PlainFile":
            print("\033[1;33m PlainFile\033[0m %s \033[1;33mcontent:\n\033[0m%s" %
                  (target_file.file_name, target_file.content))

        if target_file.get_type_name() == "DirFile":
            print(target_file.as_text())



    def edit(self, *arg):
        try:
            path = arg[0]
        except IndexError:
            print("\033[1;31m no enough args\033[0m")
            return

        file_name, work_dir, search_route = self.search_file(path)
        if work_dir == -1:
            print("\033[1;31m can't find file\033[0m")
            return

        file = self.file_manager.open_file(file_name,
                                           work_dir,
                                           self.user_manager.look_up_property(self.curr_user))
        if file is None:
            print("\033[1;31m can only edit plain text file\033[0m")
            return
        if self.user_manager.check_property(self.curr_user, file.group_id) != 0:
            print("\033[1;31m can't not access to file , have not enough auth\033[0m")
            return

        print("\033[1;33m file content:\033[0m\n%s" % file.read())
        print("\033[1;33m please input things and end up with $ in single line \033[0m")
        content = ""
        while True:
            line = input()
            if line == "$":
                file.write(content)
                break
            else:
                content += line + "\n"


    def rm(self, *arg):
        try:
            path = arg[0]
        except IndexError:
            print("\033[1;31m no enough args\033[0m")
            return

        file_name, target_file_dir, search_path = self.search_file(path)

        if target_file_dir == -1:
            print("\033[1;31m can't find file\033[0m")
            return
        work_dir = target_file_dir

        if self.file_manager.remove_file(file_name, work_dir) == -1:
            print("\033[1;31m delete file %s failed \033[0m" % file_name)
        else:
            print("\033[1;33m delete file \033[0m%s \033[1;33mok \033[0m" % file_name)



    def chmod(self, *args):
        if len(args) < 2:
            print("\033[1;31m too few args\033[0m")
            return
        file_name = args[1]
        group_id = int(args[0])
        target_file, search_route = self.file_manager.search_file(file_name, self.work_dir)
        if target_file==-1:
            print("\033[1;31m no such file \033[0m")
            return
        if self.user_manager.check_property(self.curr_user, group_id) == 0:
            target_file.set_property(group_id)
            print("\033[1;33m set\033[0m %s \033[1;33m group_id as\033[0m %d \033[1;33m ok \033[0m" % (file_name, group_id))
        else:
            print("\033[1;31m user haven't enough property\033[0m")

    def cp(self, *args):
        """
        以BFS方式复制文件
        :param args: 源文件 目标文件
        :return: 如果复制过程中出现失败 如文件有重复
                则在错误处直接停止 并提示错误信息
        """
        try:
            source_file_path = args[0]
            target_dir_path = args[1]
        except IndexError:
            print("no enough args")
            return

        file_name, file_dir, search_path = self.search_file(source_file_path)
        if file_dir == -1:
            print("can't find file")
            return
        source_file, search_path = self.file_manager.search_file(file_name, file_dir)

        file_name, file_dir, search_path = self.search_file(target_dir_path)
        if file_dir == -1:
            print("can't find file")
            return
        target_dir_file, search_path = self.file_manager.search_file(file_name, file_dir)
        if target_dir_file.get_type_name() != "DirFile":
            print("target file should be a DirFile!")
            return

        # 如果只是简单文本文件 复制 直接返回
        if source_file.get_type_name() == "PlainFile":
            if self.cp_plain_file(source_file, target_dir_file) == -1:
                print("file %s already exists in target dir %s" %
                      (source_file.file_name, target_dir_file.file_name))
            return

        # 如果是目录文件 则需要进一步复制扩展
        cp_start = self.cp_dir_file(source_file, target_dir_file)
        # 返回原目录及目标目录的DirFile对象
        if cp_start[1] == -1:
            print("file %s already exists in target dir %s" %
                  (source_file.file_name, target_dir_file.file_name))
            return

        # 使用BFS策略, 将源目录内容复制到目标目录
        cp_node_queue = [cp_start]
        while len(cp_node_queue) != 0:
            # 取出一个复制节点
            curr_cp_node_pair = cp_node_queue[0]
            curr_source_node = curr_cp_node_pair[0]
            curr_target_node = curr_cp_node_pair[1]
            cp_node_queue = cp_node_queue[1:]
            # 对当前节点进行扩展
            curr_node_children = list(curr_source_node.dir_dict.values())
            for each_child in curr_node_children:
                # 普通文本直接复制
                if each_child.get_type_name() == "PlainFile":
                    if self.cp_plain_file(each_child, curr_target_node) == -1:
                        print("file %s already exists in target dir %s" %
                              (each_child.file_name, curr_target_node.file_name))
                    continue

                if each_child.get_type_name() == "DirFile":
                    # 目录文件则需要进行拓展
                    next_cp_node_pair = self.cp_dir_file(each_child, curr_target_node)
                    if next_cp_node_pair[1] == -1:
                        print("file %s already exists in target dir %s" %
                              (each_child.file_name, curr_target_node.file_name))
                        continue
                    else:
                        cp_node_queue.append(next_cp_node_pair)
                        continue
    def chgrp(self, *args):
        if len(args) < 1:
            print("\033[1;31m too few args \033[0m")
            return

        group_id = int(args[0])
        self.user_manager.assign_user_group(self.curr_user, group_id)
        print("\033[1;33m update user group to \033[0m%d " % group_id)

    def shgrp(self):
        group_id = self.user_manager.look_up_property(self.curr_user)
        print("\033[1;33m curr user id \033[0m%d" % group_id)

    def pwd(self):
        print(self.get_wd())

    def clear(self):
        subprocess.call("clear")

    def show_blocks(self):
        print(self.file_manager.empty_block_manager.__str__())

    def show_user_history(self):
        his_list = self.user_manager.get_user_history(self.curr_user)
        print("\033[1;33m user %s action history \033[0m" % self.curr_user)
        for each in his_list:
            print("%s %s" % (each[1], each[0]))
        pass

    def tree(self):
        level_cnt = 0
        print("file_name  file type inode id")
        self.tree_walk(self.work_dir, level_cnt, True)
        return

    def tree_walk(self, curr_node, level, is_last):
        res = ""
        res += "│   " * (level - 1)

        if level != 0:
            if is_last:
                res += "└──"
            else:
                res += "├──"
        res += "%s  %s  %s" % \
               ("root" if curr_node.file_name == "" else curr_node.file_name,
                curr_node.get_type_name(),
                curr_node.inode_id)
        print(res)
        if curr_node.get_type_name() == "DirFile":
            children = tuple(curr_node.dir_dict.values())
            for each_child in range(len(children)):
                # 当为最后一个节点时
                if each_child == len(children) - 1:
                    # 且该节点为普通文本文件（不可拓展）或者是空目录时
                    # 标记为末尾文件 输出末尾文件制表符
                    if children[each_child].get_type_name() != "DirFile" or \
                            len(children[each_child].dir_dict.keys()) == 0:
                        is_last = True
                else:
                    # 反之都需要输出正常制表符
                    is_last = False
                self.tree_walk(children[each_child], level + 1, is_last)

    cmd_dict = {
        "pwd": pwd,
        "cd": cd,
        "mkdir": mkdir,
        "rm": rm,
        "edit": edit,
        "ls": ls,
        "tree": tree,
        "less": less,
        "cp": cp,
        "clear":clear,

        "chmod": chmod,
        "chgrp": chgrp,
        "shgrp": shgrp,

        "shhis": show_user_history,
        "shblk": show_blocks

    }

    ######################################################################

    def user_check_in(self):
        while True:
            print("\033[1;32m login/register: l/r \033[0m")
            act = input()
            if act == "l":
                print("\033[1;32m username: \033[0m", end="")
                username = input()
                print("\033[1;32m password: \033[0m", end="")
                password = input()
                if self.user_manager.login(username, password) != 0:
                    print("\033[1;31m login wrong \033[0m")
                    continue
                else:
                    self.curr_user = username
                    return True

            elif act == 'r':
                print("\033[1;32m username: \033[0m", end="")
                username = input()
                print("\033[1;32m password: \033[0m", end="")
                password = input()
                print("\033[1;32m confirm password: \033[0m", end="")
                conf_password = input()
                if password != conf_password:
                    print("\033[1;31m twice password are not same\033[0m")
                    continue
                if self.user_manager.register(username, password) != 0:
                    print("\033[1;31m register wrong \033[0m")
                    continue
                else:
                    self.curr_user = username
                    return True
            elif act == "e":
                return False

    def get_wd(self):
        res = ""
        for each in self.dir_route:
            res += each.file_name + "/"
        res += self.work_dir.file_name + "/"
        return res

    def search_file(self, path):
        """
        去掉目标文件得到目标文件的目录地址  先找到目标文件的目录位置 作为临时工作目录
        随后在这个工作目录 对目标文件进行打开操作
        :param path: 文件的绝对or 相对路径
        :return: 如果成功找到该文件则返回 （文件名， 其所在目录， 搜索路径）
                 没有找到则返回 -1
        """
        path = path.split("/")
        file_name = path[-1]
        tmp_path = ""
        for each in range(len(path) - 1):
            tmp_path += path[each] + "/"
        path = tmp_path

        target_dir, search_route = self.file_manager.search_file(path, self.work_dir)
        return file_name, target_dir, search_route
    def create_dir_file(self, work_dir, dir_name):
        """
        创建目录文件
        :param work_dir:
        :param dir_name:
        :return:
        """
        group_id = self.user_manager.look_up_property(self.curr_user)
        return self.file_manager.create_file("dir", dir_name, work_dir, group_id)

    def cp_plain_file(self, source, target_dir):
        """
        复制普通文本文件
        :param source: 源文件
        :param target_dir: 目标目录
        :return: -1 复制失败 0 成功
        """
        new_file = self.file_manager.open_file(source.file_name,
                                               target_dir,
                                               self.user_manager.look_up_property(self.curr_user))
        if new_file is None:
            return -1
        new_file.write(source.content)
        return 0

    def cp_dir_file(self, source, target_dir):
        """
        复制目录文件
        :param source:
        :param target_dir:
        :return: 失败时 new_dir == -1
        """
        new_dir = self.create_dir_file(target_dir, source.file_name)
        return source, new_dir