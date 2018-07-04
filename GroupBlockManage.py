
GROUP_MAX_BLOCK_CNT = 32
MAX_GROUP_CNT = 32

class GroupBlock:
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
        return  "group_id: %d\nnext_block: %d\nempty_cnt: %d\nempty_blocks: %s\n" \
                % (self.group_id, next_block, self.empty_cnt, self.empty_blocks)

class EmptyBlockManager:
    def __init__(self):
        last = None
        for i in range(MAX_GROUP_CNT):
            curr = GroupBlock(i, i*GROUP_MAX_BLOCK_CNT)
            curr.next_block = last
            last = curr
        self.super_block = last
        self.full_group = []

    def alloc_block(self):
        get_block = self.super_block.acquire_block()
        if self.super_block.empty_cnt == 0:
            self.full_group.append(self.super_block)
            self.super_block = self.super_block.next_block
        return get_block

    def free_block(self, *blocks):
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
            res += curr.__str__() + "\n\n"
            curr = curr.next_block
        return  res

