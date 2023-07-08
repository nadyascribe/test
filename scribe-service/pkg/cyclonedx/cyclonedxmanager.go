package cyclonedx

import (
	"bufio"
	"bytes"
	"encoding/base64"
	"fmt"
	"io"
	"os"
	"path"
	"strings"

	cdx "github.com/CycloneDX/cyclonedx-go"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
	"github.com/scribe-security/scribe2/scribe-service/pkg/slicesh"
)

const (
	JsonFormat = "cyclonedxjson" //nolint:stylecheck,revive
	XmlFormat  = "cyclonedxxml"  //nolint:stylecheck,revive
	extJSON    = ".json"
	extXML     = ".xml"
)

type CycloneDxManager struct { //nolint:revive
	Option string
	Ext    string
	Format cdx.BOMFileFormat
}

func NewCycloneDxManager(option string) (*CycloneDxManager, error) {
	ext, format, err := GetSbomExt(option)
	if err != nil {
		return nil, err
	}
	return &CycloneDxManager{
		Option: option,
		Ext:    ext,
		Format: format,
	}, nil
}

func GetSbomExt(option string) (string, cdx.BOMFileFormat, error) {
	var format cdx.BOMFileFormat
	var ext string
	switch option {
	case JsonFormat:
		ext = extJSON
		format = cdx.BOMFileFormatJSON
	case XmlFormat:
		ext = extXML
		format = cdx.BOMFileFormatXML
	default:

		return "", cdx.BOMFileFormatJSON, fmt.Errorf(
			"cyclonedx - Unknown presenter, type: %s",
			option,
		)
	}

	return ext, format, nil
}

func GetSbomFileExt(fileName string) (extension string, err error) {
	fileExt := strings.ToLower(path.Ext(fileName))
	switch fileExt {
	case extJSON:
		return JsonFormat, nil
	case extXML:
		return XmlFormat, nil
	}
	return "", fmt.Errorf("unsuported SBOM file extension: %s", fileExt)
}

func (pres *CycloneDxManager) GetName(bom *cdx.BOM) (string, error) {
	var name string
	switch bom.Metadata.Component.Group {
	case "image":
		name = bom.Metadata.Component.Version
	case "directory":
		name = bom.Metadata.Component.Name
	default:
		return "", fmt.Errorf("Unknown sbom group %s", bom.Metadata.Component.Group) //nolint:stylecheck
	}

	return name, nil
}

func (pres *CycloneDxManager) Decode(reader io.Reader, bom *cdx.BOM) error {
	decoder := cdx.NewBOMDecoder(reader, pres.Format)

	return decoder.Decode(bom)
}

func (pres *CycloneDxManager) Encode(writer io.Writer, bom *cdx.BOM) error {
	encoder := cdx.NewBOMEncoder(writer, pres.Format)
	encoder.SetPretty(true)

	return encoder.Encode(bom)
}

func (pres *CycloneDxManager) ReadFromFile(pth string, bom *cdx.BOM) error {
	f, err := os.OpenFile(pth, os.O_RDONLY, 0o644) //nolint:gomnd
	if err != nil {
		return err
	}

	defer f.Close()

	r := bufio.NewReader(f)
	return pres.Decode(r, bom)
}

func (pres *CycloneDxManager) WriteToFile(pth string, bom *cdx.BOM) error {
	f, err := os.OpenFile(pth, os.O_CREATE|os.O_RDWR, 0o644) //nolint:gomnd
	if err != nil {
		return err
	}

	defer f.Close()

	w := bufio.NewWriter(f)

	defer w.Flush()

	log.S().Infof("Cyclonedx - Sbom pushed to FS, format: %s, Path: %s", pres.Option, pth)
	return pres.Encode(w, bom)
}

func (pres *CycloneDxManager) WriteOut(outputList []string, bom *cdx.BOM) error {
	for _, path := range outputList {
		if path != "" {
			err := pres.WriteToFile(path, bom)
			if err != nil {
				log.S().Warnf("presenter - cyclonedx - write out fail, Path: %s", path)
				return err
			}
		}
	}

	return nil
}

func (pres *CycloneDxManager) ExtractConcise(reader io.Reader) (*bytes.Buffer, error) {
	var bom cdx.BOM
	if err := pres.Decode(reader, &bom); err != nil {
		return nil, err
	}

	bom.Components = slicesh.FilterBy(bom.Components, func(comp *cdx.Component) bool {
		return comp.Type == cdx.ComponentTypeFile
	})

	bom.Dependencies = slicesh.FilterBy(bom.Dependencies, func(dep *cdx.Dependency) bool {
		if strings.HasPrefix(dep.Ref, "pkg:file") {
			return true
		}

		dep.Dependencies = slicesh.FilterBy(dep.Dependencies, func(subDep *string) bool {
			return strings.HasPrefix(*subDep, "pkg:file")
		})

		if dep.Dependencies != nil && len(*dep.Dependencies) == 0 {
			dep.Dependencies = nil
		}

		return false
	})

	bb := new(bytes.Buffer)
	if err := pres.Encode(bb, &bom); err != nil {
		return nil, err
	}
	return bb, nil
}

// ExtractSyft from the cyclonedx bom as reader
func (pres *CycloneDxManager) ExtractSyft(reader io.Reader) (io.Reader, error) {
	var bom cdx.BOM
	if err := pres.Decode(reader, &bom); err != nil {
		return nil, err
	}

	if bom.Components == nil {
		return nil, fmt.Errorf("no components found in the SBOM")
	}

	c := *bom.Components
	for i := range c {
		if c[i].Group == "syft" {
			for _, prop := range *c[i].Properties {
				if prop.Name != "content" {
					continue
				}

				buff := strings.NewReader(prop.Value)
				return base64.NewDecoder(base64.StdEncoding, buff), nil
			}
		}
	}
	return nil, fmt.Errorf("syft section not found")
}
