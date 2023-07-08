//nolint
package slicesh

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRemoveBySwapWithLast(t *testing.T) {
	type args struct {
		s []int
		i int
	}
	type testCase struct {
		name string
		args args
		want []int
	}
	tests := []testCase{
		{
			name: "nil",
			args: args{
				s: nil,
				i: 0,
			},
			want: nil,
		},
		{
			name: "nil_neg_i",
			args: args{
				s: nil,
				i: -1,
			},
			want: nil,
		},
		{
			name: "nil_invalid_i",
			args: args{
				s: nil,
				i: 1000,
			},
			want: nil,
		},
		{
			name: "empty",
			args: args{
				s: []int{},
				i: 0,
			},
			want: []int{},
		},
		{
			name: "empty_neg_i",
			args: args{
				s: []int{},
				i: -1,
			},
			want: []int{},
		},
		{
			name: "empty_invalid_i",
			args: args{
				s: []int{},
				i: 1000,
			},
			want: []int{},
		},
		{
			name: "len_1",
			args: args{
				s: []int{1},
				i: 0,
			},
			want: []int{},
		},
		{
			name: "len_1_neg_i",
			args: args{
				s: []int{1},
				i: -1,
			},
			want: []int{1},
		},
		{
			name: "len_1_invalid_i",
			args: args{
				s: []int{1},
				i: 1000,
			},
			want: []int{1},
		},
		{
			name: "len_4_0",
			args: args{
				s: []int{1, 3, 5, 7},
				i: 0,
			},
			want: []int{7, 3, 5},
		},
		{
			name: "len_4_2",
			args: args{
				s: []int{1, 3, 5, 7},
				i: 2,
			},
			want: []int{1, 3, 7},
		},
		{
			name: "len_4_neg_i",
			args: args{
				s: []int{1, 3, 5, 7},
				i: -1,
			},
			want: []int{1, 3, 5, 7},
		},
		{
			name: "len_4_invalid_i",
			args: args{
				s: []int{1, 3, 5, 7},
				i: 1000,
			},
			want: []int{1, 3, 5, 7},
		},
		{
			name: "len_10_2",
			args: args{
				s: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
				i: 2,
			},
			want: []int{-11, 999, 3213, 8, 3, 6, -9, -123213},
		},
		{
			name: "len_10_0",
			args: args{
				s: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
				i: 0,
			},
			want: []int{3213, 999, 1000, 8, 3, 6, -9, -123213},
		},
		{
			name: "len_10_9",
			args: args{
				s: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
				i: 9,
			},
			want: []int{-11, 999, 1000, 8, 3, 6, -9, -123213},
		},
		{
			name: "len_10_10_invalid",
			args: args{
				s: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
				i: 10,
			},
			want: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
		},
		{
			name: "len_10_7",
			args: args{
				s: []int{-11, 999, 1000, 8, 3, 6, -9, -123213, 3213},
				i: 7,
			},
			want: []int{-11, 999, 1000, 8, 3, 6, -9, 3213},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := RemoveBySwapWithLast(tt.args.s, tt.args.i)
			assert.Len(t, got, len(tt.want))
			assert.ElementsMatch(t, got, tt.want)
		})
	}
}
