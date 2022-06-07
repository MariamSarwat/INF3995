#ifndef BUF_H
#define BUF_H

/*
 * SPDX-License-Identifier: GPL-2.0-only
 *
 * Copyright (c) 2020 Olivier Dion <olivier.dion@polymtl.ca>
 *
 * utils/buf.h - Stretch buffer
 *
 * Stretch buffer are like stack.  You can push and pop them.  What's
 * nice about them is that you can manipulate the raw pointer. Thus,
 * you can use direct access with [] if you're sure that the index is
 * in range.
 *
 * Stretch buffer are also generic, and do type checking, refusing to
 * compile if you got it wrong. Who needs template?
 *
 * To use them, you should first declare a pointer to some type.
 * Then, you can use the buf_new() to dynamically allocate a new
 * buffer for that type.  When done, use buf_del() on the same
 * pointer.
 *
 * You can buf_push(), buf_pop() and buf_peek() on a buffer, you can
 * also buf_clear() and buf_fit() them.
 *
 * Finally, it's possible to iterate over a buffer with buf_for_each()
 * and buf_for_each_reverse().
 */

#include <string.h>

#if !defined(BUF_MALLOC) || !defined(BUF_FREE) || !defined(BUF_REALLOC)
#  define BUF_MALLOC malloc
#  define BUF_FREE free
#  define BUF_REALLOC realloc
#  include <malloc.h>
#endif

#ifndef CONFIG_RELEASE
#  define BUF_DEFAULT_SIZE 1
#else
#  define BUF_DEFAULT_SIZE 16
#endif

struct buf {
	usize count;
	usize len;
	char blob[];
};

/* Helpers */
#define buf_padding(_buf)   paddingof(struct buf, typeof(*(_buf)))
#define buf_sizeof(_buf)    sizeof(*(_buf))
#define buf_typeof(_buf)    typeof(*(_buf))
#define buf_container(_buf) container_of(((void*)_buf) - buf_padding(_buf), struct buf, blob)


static inline void *buf_new(unsigned esize, unsigned padding)
{
	struct buf *container = calloc(sizeof(struct buf) + padding + BUF_DEFAULT_SIZE * esize, 1);
	container->count = 0;
	container->len = BUF_DEFAULT_SIZE;
	return container->blob + padding;
}
#define buf_new(buf) buf = buf_new(buf_sizeof(buf), buf_padding(buf))

#define buf_del(buf) BUF_FREE(buf_container(buf))

static inline void *buf_push(struct buf *container, void *elem, usize esize, usize padding)
{
	if (container->count == container->len) {
		usize len = container->len << 1;
		container = BUF_REALLOC(container, sizeof(struct buf) + padding + len * esize);
		container->len = len;
	}
	memcpy(container->blob + padding + container->count * esize, elem, esize);
	++container->count;
	return container->blob + padding;
}
#define buf_push(buf, elem)						\
	({								\
		_Static_assert(typecheck(*(buf), *(elem)), "buf typecheck failed"); \
		buf = (buf_typeof(buf)*)buf_push(buf_container(buf),	\
						elem, buf_sizeof(buf), buf_padding(buf)); \
	})


static inline void *buf_pushv(struct buf *container, void *elem, usize cnt, usize esize, usize padding)
{
	if (container->count + cnt  >= container->len) {

		usize len;

		len = container->len;

		do {
			len <<= 1;
		} while (container->count + cnt >= len);

		container = BUF_REALLOC(container, sizeof(struct buf) + padding + len * esize);
		container->len = len;
	}

	for (usize i=0; i<cnt; ++i) {
		memcpy(container->blob + padding + (container->count + i) * esize,
			elem, esize);
		++elem;
	}

	container->count += cnt;

	return container->blob + padding;
}
#define buf_pushv(buf, elem, cnt)					\
	({								\
		_Static_assert(typecheck(*(buf), *(elem)), "buf typecheck failed"); \
		buf = (buf_typeof(buf)*)buf_pushv(buf_container(buf),	\
						elem, cnt, buf_sizeof(buf), buf_padding(buf)); \
	})

static inline void *buf_peek(struct buf *container, usize esize, usize padding)
{
	if (0 == container->count) {
		return NULL;
	}

	return (void*)(container->blob + padding + esize * (container->count - 1));
}
#define buf_peek(buf) *((buf_typeof(buf)*)buf_peek(buf_container(buf), buf_sizeof(buf), buf_padding(buf)))

static inline void *buf_pop(struct buf *container, usize esize, usize padding)
{
	if (0 == container->count) {
		return NULL;
	}
	return (void*)(container->blob + padding + esize * --container->count);
}
#define buf_pop(buf) *((buf_typeof(buf)*)buf_pop(buf_container(buf), buf_sizeof(buf), buf_padding(buf)))

static inline void buf_clear(struct buf *container)
{
	container->count = 0;
}
#define buf_clear(buf) buf_clear(buf_container(buf))

static inline void *buf_fit(struct buf *container, usize esize, usize padding)
{
	container->len = container->count;
	container = BUF_REALLOC(container,
				sizeof(struct buf) +
				padding +
				container->len * esize);
	return container->blob + padding;
}
#define buf_fit(buf) buf = buf_fit(buf_container(buf), buf_sizeof(buf), buf_padding(buf))

__pure
static inline usize buf_cnt(struct buf *container)
{
	return container->count;
}
#define buf_cnt(buf) buf_cnt(buf_container(buf))

#define buf_for_each(pos, buf) _Static_assert(typecheck(*(buf), *(pos)), "buf typecheck");  pos=&buf[0]; for (usize __$i=0; __$i++<buf_cnt(buf); pos=&buf[__$i])
#define buf_for_each_reverse(pos, buf) _Static_assert(typecheck(*(buf), *(pos)), "buf typecheck"); pos=buf_peek(buf); for (isize __$i=buf_cnt(buf)-1; __$i-->=0; pos=&buf[__$i])


#endif
