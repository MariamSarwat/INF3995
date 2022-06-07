#ifndef BTREE_H
#define BTREE_H

struct btree {
	struct btree *lt, *gt;
	u64 key;
};

/**
 * btree_kinit() - Initialize @node with @key
 */
static inline void btree_kinit(u64 key, struct btree *node)
{
	node->lt  = NULL;
	node->gt  = NULL;
	node->key = key;
}

/**
 * btree_add() - Add node to a binary tree.
 *
 * @node : The node to add
 * @head : Pointer to the root of the tree
 *
 * Return: 0 on success, -1 if there was a key collision.  @node is
 * only added to the tree on success.
 */
extern int btree_add(struct btree *node, struct btree **head) __notnull;

/**
 * btree_rm() - Remove a node from a binary tree.
 *
 * @key  : The key of the node to remove
 * @head : Pointer to the root of the tree
 *
 * Return: Pointer to the removed node on success, %NULL if no node
 * with @key exists in the tree pointed by @head.
 */
extern struct btree *btree_rm(u64 key, struct btree **head) __notnull;

/**
 * btree_find() - Find a node in a binary tree.
 *
 * @key  : The key of the node to find
 * @head : Root of the tree.
 *
 * Return: Pointer to the searched node with @key on succes, %NULL if
 * no node with @key exists in tree @head
 */
extern struct btree *btree_find(u64 key, const struct btree *head) __pure;

#define btree_for_each(IT, HEAD, MEMBER)		 \
	for (IT=btree_it_init())			 \

#endif
