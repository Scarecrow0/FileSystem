"""
使用成组链接法管理空闲块
"""

GROUP_MAX_BLOCK_CNT = 32
MAX_GROUP_CNT = 32


class GroupBlock:
    """
    成组链接法中的每一块
    """

    def __init__(self, group_id, curr_block_id):
        self.group_id = group_id
        self.next_block = None
        self.empty_blocks = []
        for i in range(GROUP_MAX_BLOCK_CNT):
            self.empty_blocks.append(curr_block_id + i)
        self.empty_cnt = len(self.empty_blocks)

    def acquire_block(self):
        self.empty_cnt -= 1
        return self.empty_blocks.pop()

    def recycle_block(self, block_id):
        self.empty_cnt += 1
        self.empty_blocks.append(block_id)

    def __str__(self):
        if self.next_block is not None:
            next_block = self.next_block.group_id
        else:
            next_block = -1
        return "group_id: %d\nnext_block: %d\nempty_cnt: %d\nempty_blocks: %s\n" \
               % (self.group_id, next_block, self.empty_cnt, self.empty_blocks)


class EmptyBlockManager:
    """
    空闲块的成组链接
    """

    def __init__(self):
        last = None
        # 初始化过程 ：
        # 依次创建各个块，并依次连接起来
        for i in range(MAX_GROUP_CNT):
            curr = GroupBlock(i, i * GROUP_MAX_BLOCK_CNT)
            curr.next_block = last
            last = curr
        self.super_block = last
        self.full_group = []

    def alloc_block(self):
        """
        分配空间 从超级块中分配空闲块 如果超级块没有空闲块了
        载入下个组作为超级块，并将已满的超级块引用放入已满队列
        :return:
        """
        get_block = self.super_block.acquire_block()
        if self.super_block.empty_cnt == 0:
            self.full_group.append(self.super_block)
            self.super_block = self.super_block.next_block
        return get_block

    def free_block(self, *blocks):
        """
        释放空间 将传入的块号重新链接回超级块
        如果超级块链接空闲块已满 ，则从已满队列中取出一个组载入超级块
        将已满超级块链在其后
        :param blocks:
        :return:
        """
        for each_block in blocks:
            self.super_block.recycle_block(each_block)
            if self.super_block.empty_cnt == 32:
                next_super_block = self.full_group.pop()
                next_super_block.next_block = self.super_block
                self.super_block = next_super_block

    def __str__(self):
        res = ""
        res += "super_block %s\n" % self.super_block.__str__()
        curr = self.super_block.next_block
        while curr is not None:
            if curr.empty_cnt < 32:
                res += curr.__str__() + "\n"
            curr = curr.next_block
        return res
