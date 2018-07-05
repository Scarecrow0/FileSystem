# FileSystem

运行要求  Python 3 

文件操作

    cd 相对绝对路径
    pwd 输出当前工作目录
    ls  查看当前目录中的文件
    edit 创建修改文件 相对绝对路径
    mkdir 创建目录 当前目录
    rm 删除文件 目录 相对绝对路径
    shhis 显示用户的历史操作
    tree 以DFS方式输出目录情况 

系统信息操作
    
    shblk 显示当前的成组链接法空余块的情况

权限操作
    
    权限由用户权限组方式进行管理，由一个组号表示文件或者用户所属的组
    只有用户的组号高于文件组号 方可进行访问
    
    chgrp  更改当前用户所在用户组
    shgrp  显示用户当前权限组
    chmod  更改文件所属于的权限组
    


目前由 命令行模块，文件系统模块， 空闲块管理模块组成