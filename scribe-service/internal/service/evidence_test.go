package service

import (
	"fmt"
	"testing"
	"time"

	"github.com/google/uuid"
)

//nolint:lll
func Test_validateInput(t *testing.T) {
	testCases := []struct {
		input    string
		expected string
	}{
		{"https://github.com/scribe-security/scribe-node-demo.git", "https\\u003A\\u002F\\u002Fgithub.com\\u002Fscribe-security\\u002Fscribe-node-demo.git"},
		{"ValidName123_@~![]&#+, ", "ValidName123_@~![]&#+,"},
		{"InvalidName$", "InvalidName\\u0024"},
		{" ", ""},
		{"", ""},
		{"A", "A"},
		{"1", "1"},
		{".", "."},
		{"%", "%"},
		{"-", "-"},
		{"_", "_"},
		{"@", "@"},
		{"~", "~"},
		{"!", "!"},
		{"=", "="},
		{"[", "["},
		{"]", "]"},
		{"&", "&"},
		{"#", "#"},
		{"+", "+"},
		{",", ","},
		{"A ", "A"},
		{" A", " A"},
		{" A ", " A"},
		{"  A  ", "  A"},
		{"A 1", "A 1"},
		{"A1  ", "A1"},
		{"  A1", "  A1"},
		{"  A 1  ", "  A 1"},
		{"A  1", "A  1"},
		{"A1  ", "A1"},
		{"  A1", "  A1"},
		{"  A  1  ", "  A  1"},
		{"A   1", "A   1"},
		{"A1   ", "A1"},
		{"   A1", "   A1"},
		{"   A   1   ", "   A   1"},
		{"Valid$Name", "Valid\\u0024Name"},
		{"Invalid#Name", "Invalid#Name"},
		{"Invalid^Name", "Invalid\\u005EName"},
		{"Invalid{Name", "Invalid\\u007BName"},
		{"Invalid}Name", "Invalid\\u007DName"},
		{"Invalid|Name", "Invalid\\u007CName"},
		{"Invalid;Name", "Invalid\\u003BName"},
		{"Invalid:Name", "Invalid\\u003AName"},
		{"Invalid<Name", "Invalid\\u003CName"},
		{"Invalid>Name", "Invalid\\u003EName"},
		{"Invalid/Name", "Invalid\\u002FName"},
		{"Invalid?Name", "Invalid\\u003FName"},
		{"Invalid\"Name", "Invalid\\u0022Name"},
		{"Invalid'Name", "Invalid\\u0027Name"},
		{"<Invalid}Nam?e", "\\u003CInvalid\\u007DNam\\u003Fe"},
		{"<Invalid|Nam?e", "\\u003CInvalid\\u007CNam\\u003Fe"},
		{"<Invalid}Nam?e     ", "\\u003CInvalid\\u007DNam\\u003Fe"},
		{"<Invalid|Nam?e           ", "\\u003CInvalid\\u007CNam\\u003Fe"},
		{"Invalid Name$", "Invalid Name\\u0024"},
		{"$Invalid Name", "\\u0024Invalid Name"},
		{"Inva$lid Name", "Inva\\u0024lid Name"},
		{"Invalid Name$", "Invalid Name\\u0024"},
		{"$Invalid Name", "\\u0024Invalid Name"},
		{"Inva$lid Name", "Inva\\u0024lid Name"},
		{"Invalid Name$", "Invalid Name\\u0024"},
		{"$Invalid Name", "\\u0024Invalid Name"},
		{"Inva$lid Name", "Inva\\u0024lid Name"},
	}

	for _, testCase := range testCases {
		result := validateInput(testCase.input)
		if result != testCase.expected {
			t.Errorf("Test failed for input '%s': expected %s, got %s", testCase.input, testCase.expected, result)
		}
	}
}

//nolint:funlen
func Test_getPipelineRunParams(t *testing.T) {
	testCases := []struct {
		contextData map[string]interface{}
		expected    PipelineParams
	}{
		{
			map[string]interface{}{
				"name":            "ValidName",
				"pipeline_name":   "ValidPipeline",
				"run_id":          "ValidRunID",
				"product_version": "ValidVersion",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				PipelineRun:  "ValidRunID",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "InvalidName$",
				"pipeline_name":   "InvalidPipeline$",
				"run_id":          "InvalidRunID$",
				"product_version": "InvalidVersion$",
			},
			PipelineParams{
				ProductKey:   "InvalidName\\u0024",
				PipelineName: "InvalidPipeline\\u0024",
				PipelineRun:  "InvalidRunID\\u0024",
				Version:      "InvalidVersion\\u0024",
			},
		},
		{
			map[string]interface{}{
				"name":            "InvalidName$     ",
				"pipeline_name":   "InvalidPipeline$      ",
				"run_id":          "InvalidRunID$      ",
				"product_version": "InvalidVersion$      ",
			},
			PipelineParams{
				ProductKey:   "InvalidName\\u0024",
				PipelineName: "InvalidPipeline\\u0024",
				PipelineRun:  "InvalidRunID\\u0024",
				Version:      "InvalidVersion\\u0024",
			},
		},
		{
			map[string]interface{}{
				"name":            "$InvalidName     ",
				"pipeline_name":   "$InvalidPipeline      ",
				"run_id":          "$InvalidRunID      ",
				"product_version": "$InvalidVersion      ",
			},
			PipelineParams{
				ProductKey:   "\\u0024InvalidName",
				PipelineName: "\\u0024InvalidPipeline",
				PipelineRun:  "\\u0024InvalidRunID",
				Version:      "\\u0024InvalidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "$Invalid;Name     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "\\u0024Invalid\\u003BName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "$;     ",
				"pipeline_name":   "$;        ",
				"run_id":          "$;       ",
				"product_version": "$;          ",
			},
			PipelineParams{
				ProductKey:   "\\u0024\\u003B",
				PipelineName: "\\u0024\\u003B",
				PipelineRun:  "\\u0024\\u003B",
				Version:      "\\u0024\\u003B",
			},
		},
		{
			map[string]interface{}{},
			PipelineParams{
				ProductKey:   "",
				PipelineName: "",
				PipelineRun:  "",
				Version:      "",
			},
		},
		{
			map[string]interface{}{
				"name":            "     ",
				"pipeline_name":   "$;        ",
				"run_id":          "$;       ",
				"product_version": "$;          ",
			},
			PipelineParams{
				ProductKey:   "",
				PipelineName: "\\u0024\\u003B",
				PipelineRun:  "\\u0024\\u003B",
				Version:      "\\u0024\\u003B",
			},
		},
		{
			map[string]interface{}{
				"name":            "$Invalid;Name     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "\\u0024Invalid\\u003BName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"pipeline_name":   "ValidPipeline",
				"run_id":          "ValidRunID",
				"product_version": "ValidVersion",
			},
			PipelineParams{
				ProductKey:   "",
				PipelineName: "ValidPipeline",
				PipelineRun:  "ValidRunID",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"git_url":         "ValidName",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"git_url":         "https://github.com/scribe-security/scribe-node-demo.git",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "https\\u003A\\u002F\\u002Fgithub.com\\u002Fscribe-security\\u002Fscribe-node-demo.git",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"git_url":         "",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"git_url":         "$Invalid;Name     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "\\u0024Invalid\\u003BName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"git_url":         "somegit$Invalid;Name1     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "",
				"git_url":         "somegit$Invalid;Name2     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "somegit\\u0024Invalid\\u003BName2",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "    ",
				"git_url":         "somegit$Invalid;Name3     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "somegit\\u0024Invalid\\u003BName3",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "    ",
				"dir_path":        "somedirpath$Invalid;Name     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "somedirpath\\u0024Invalid\\u003BName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "    ",
				"dir_path":        "somedirpath$Invalid;Name     ",
				"git_url":         "somegit$Invalid;Name4     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "somegit\\u0024Invalid\\u003BName4",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "    ",
				"dir_path":        "somedirpath$Invalid;Name     ",
				"git_url":         "     ",
				"pipeline_name":   "$Invalid;Pipeline      ",
				"run_id":          "$Invalid;RunID      ",
				"product_version": "$Invalid;Version      ",
			},
			PipelineParams{
				ProductKey:   "somegit\\u0024Invalid\\u003BName",
				PipelineName: "\\u0024Invalid\\u003BPipeline",
				PipelineRun:  "\\u0024Invalid\\u003BRunID",
				Version:      "\\u0024Invalid\\u003BVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"pipeline_name":   "Valid$Pipeline",
				"workflow":        "ValidWorkflow",
				"context_type":    "ValidContextType",
				"run_id":          "ValidRunID",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "Valid\\u0024Pipeline",
				PipelineRun:  "ValidRunID",
				Version:      "ValidVersion",
			},
		},

		{
			map[string]interface{}{
				"name":            "ValidName",
				"workflow":        "Valid$Workflow",
				"context_type":    "ValidContextType",
				"run_id":          "ValidRunID",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "Valid\\u0024Workflow",
				PipelineRun:  "ValidRunID",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"context_type":    "ValidContextType",
				"run_id":          "Valid$RunID",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidContextType",
				PipelineRun:  "Valid\\u0024RunID",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"pipeline_name":   "ValidPipeline",
				"workflow":        "ValidWorkflow",
				"context_type":    "ValidContextType",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"pipeline_name":   "ValidPipeline",
				"workflow":        "ValidWorkflow",
				"context_type":    "Valid$ContextType",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":            "ValidName",
				"pipeline_name":   "ValidPipeline",
				"workflow":        "ValidWorkflow",
				"product_version": "ValidVersion",
				"sbomversion":     "ValidSBOMVersion",
				"timestamp":       "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				Version:      "ValidVersion",
			},
		},
		{
			map[string]interface{}{
				"name":          "ValidName",
				"pipeline_name": "ValidPipeline",
				"workflow":      "ValidWorkflow",
				"context_type":  "ValidContextType",
				"run_id":        "ValidRunID",
				"sbomversion":   "Valid$SBOMVersion",
				"timestamp":     "ValidTimestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				PipelineRun:  "ValidRunID",
				Version:      "Valid\\u0024SBOMVersion",
			},
		},
		{
			map[string]interface{}{
				"name":          "ValidName",
				"pipeline_name": "ValidPipeline",
				"workflow":      "ValidWorkflow",
				"context_type":  "ValidContextType",
				"run_id":        "ValidRunID",
				"timestamp":     "Valid$Timestamp",
			},
			PipelineParams{
				ProductKey:   "ValidName",
				PipelineName: "ValidPipeline",
				PipelineRun:  "ValidRunID",
				Version:      "Valid\\u0024Timestamp",
			},
		},
	}

	for _, testCase := range testCases {
		var teamID int64 = 1
		var validatedProductKey string
		contextKeysToCheck := []string{"name", "git_url", "input_name", "target_git_url", "dir_path", "file_path"}
		for _, key := range contextKeysToCheck {
			if value, ok := testCase.contextData[key].(string); ok {
				if value != "" && validateInput(value) != "" {
					validatedProductKey = validateInput(value)
					break
				}
			}
		}
		if validatedProductKey != "" {
			uniqueKey := fmt.Sprintf("%d%s", teamID, validatedProductKey)
			testCase.expected.ProductKey = uuid.NewSHA1(uuid.NameSpaceOID, []byte(uniqueKey)).String()
		}

		if testCase.contextData["run_id"] == nil {
			t := time.Now()
			rounded := t.Add(-time.Duration(t.Minute()%10) * time.Minute).Truncate(10 * time.Minute)
			if testCase.contextData["context_type"] != nil {
				testCase.expected.PipelineRun = fmt.Sprintf("%s %s", validateInput(testCase.contextData["context_type"].(string)), rounded.String())
			} else {
				testCase.expected.PipelineRun = rounded.String()
			}
		}

		result := getPipelineRunParams(testCase.contextData, teamID)
		if result != testCase.expected {
			t.Errorf("\nTest failed for input '%v': \nexpected %v, \ngot validatedProductKey %v\ngot %v",
				testCase.contextData, testCase.expected, validatedProductKey, result)
		}
	}
}
