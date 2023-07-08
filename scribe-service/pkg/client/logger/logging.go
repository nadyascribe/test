package logger

import (
	"github.com/sirupsen/logrus"
)

// logging contains all logging-related configuration options available to the user via the application config.
type Logging struct {
	Structured   bool         `yaml:"structured" json:"structured" mapstructure:"structured"` // show all log entries as JSON formatted strings
	LevelOpt     logrus.Level `yaml:"-" json:"-"`                                             // the native log level object used by the logger
	Level        string       `yaml:"level" json:"level" mapstructure:"level"`                // the log level string hint
	FileLocation string       `yaml:"file" json:"file-location" mapstructure:"file"`          // the file path to write logs to
}

type LogName struct {
	HeaderType string
	ID1        string
	ID2        string
	ID3        string
	ID4        string
	Extra      logrus.Fields
}
