package ttools

// StrRef returns reference of the string argument
func StrRef(s string) *string { return &s }

// IntRef returns reference of the int argument
func IntRef(i int) *int { return &i }
