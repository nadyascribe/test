package slicesh

// RemoveBySwapWithLast replaces element of a given slice on index `i` by the last element and reduces slice size by one.
// So yes, it changes elements order.
// it does nothing if `i` is invalid (less than 0 or greater than slice's size).
func RemoveBySwapWithLast[S ~[]E, E any](s S, i int) S {
	ll := len(s)

	switch {
	case i < 0 || i > ll: // invalid `i`
		return s
	case ll == 0:
		return s
	case ll-2 >= i: // otherwise we are on the last element, just reduce slice size
		s[i] = s[ll-1]
	}

	s = s[:ll-1]
	return s
}

// FilterBy traverses slice `S` and removes element from it if `filter` returns `true`.
// Does not respect elements order.
func FilterBy[S ~[]E, E any](s *S, filter func(*E) bool) *S {
	idx := 0
	for {
		if s == nil || len(*s)-1 < idx {
			break
		}
		el := (*s)[idx]
		if !filter(&el) {
			// increase only if nothing is changed on the current iteration
			// otherwise we need to check the current index again because it's changed by the last slice's element
			idx++
			continue
		}

		*s = RemoveBySwapWithLast(*s, idx)
	}
	return s
}
