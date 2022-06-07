/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 *
 * utils/btree.c - Simple binary tree.
 *
 * Key are encoded on 64 bits.	Collisions are not authorized and
 * result in an error.	Thus, the tree is guaranteed to have key
 * uniquess between node.
 *
 * Propably not the best implementation.  If you're looking for a tree
 * with a lots of write operations, use a Red-Black tree instead.  For
 * a tree with lots of read operations, prefer an AVL tree.
 *
 * Usage:
 *
 * You should embed a struct btree in your own structure.  You can
 * then add this structure to a tree and retrieve it later.  Since
 * this is composition, your can retrieve your original structure
 * using the container_of() macro.
 */

#include "utils/btree.h"

int btree_add(struct btree *node, struct btree **phead)
{
	u64 key = node->key;

	for (struct btree *head=*phead; head; head=*phead) {

		/* Violation of uniqueness of keys */
		if (unlikely(head->key == key)) {
			return -1;
		}

		if (key < head->key) {
			phead = &head->lt;
		} else {
			phead = &head->gt;
		}
	}

	*phead = node;

	return 0;
}

struct btree *btree_rm(u64 key, struct btree **phead)
{
	struct btree **root = phead;

	for (struct btree *head=*phead; head; head = *phead) {

		if (key < head->key) {
			phead = &head->lt;
			continue;
		} else if (key > head->key) {
			phead = &head->gt;
			continue;
		}

		if (head->lt) {
			*phead = head->lt;
			if (head->gt) {
				btree_add(head->gt, root);
			}
		} else if (head->gt) {
			*phead = head->gt;
		} else {
			*phead = NULL;
		}

		head->lt = NULL;
		head->gt = NULL;

		return head;
	}

	return NULL;
}

struct btree *btree_find(u64 key, const struct btree *head)
{
	while (head) {
		if (head->key == key) {
			break;
		}
		if (key < head->key) {
			head = head->lt;
		} else {
			head = head->gt;
		}
	}

	return (struct btree*)head;
}
