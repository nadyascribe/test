package domain

type Synopsis struct {
	OperatingSystem  string     `json:"operatingSystem"`
	Licenses         []*License `json:"licenses"`
	LayersCount      int        `json:"layersCount"`
	TotalPackages    int        `json:"totalPackages"`
	NewPackages      int        `json:"newPackages"`
	ModifiedPackages int        `json:"modifiedPackages"`
	RemovedPackages  int        `json:"removedPackages"`
}

type License struct {
	Name  string `json:"name,omitempty"`
	Count int    `json:"count,omitempty"`
}
