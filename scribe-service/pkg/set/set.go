package set

import "golang.org/x/exp/maps"

type Set[T comparable] map[T]struct{}

func New[T comparable]() Set[T] {
	return make(Set[T])
}

func FromValues[T comparable](values ...T) Set[T] {
	s := make(Set[T], len(values))
	for _, k := range values {
		s.add(k)
	}
	return s
}

func (s Set[T]) Add(v T) bool {
	prevLen := len(s)
	s.add(v)
	return prevLen != len(s)
}

func (s Set[T]) add(v T) {
	s[v] = struct{}{}
}

func (s Set[T]) Len() int {
	return len(s)
}

func (s *Set[T]) Clear() {
	*s = make(Set[T])
}

func (s Set[T]) Clone() Set[T] {
	clonedSet := make(Set[T], s.Len())
	for elem := range s {
		clonedSet.add(elem)
	}
	return clonedSet
}

func (s Set[T]) Contains(v ...T) bool {
	for _, val := range v {
		if _, ok := s[val]; !ok {
			return false
		}
	}
	return true
}

func (s Set[T]) Pop() (v T, ok bool) {
	for item := range s {
		delete(s, item)
		return item, true
	}
	return
}

func (s Set[T]) Remove(v T) {
	delete(s, v)
}

func (s Set[T]) ToSlice() []T {
	return maps.Keys(s)
}
