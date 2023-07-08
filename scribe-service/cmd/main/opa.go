package main

import (
	"log"

	"github.com/spf13/cobra"

	"github.com/scribe-security/scribe2/scribe-service/internal/rego"
)

var (
	provenanceFileURL string
	protectedBranch   string
	token             string
	policyPath        string
	buildScriptPath   string
	repositoryName    string
	repositoryURL     string
	debug             bool
	// provenanceURL     string
	outFile string
)

// sigVerifyCmd represents the sigVerify command
var opaCmd = &cobra.Command{
	Use: "opa",
	Run: func(cmd *cobra.Command, args []string) {
		err := rego.InvokePolicy(
			cmd.Context(),
			provenanceFileURL,
			protectedBranch,
			token,
			policyPath,
			buildScriptPath,
			repositoryName,
			repositoryURL,
			debug,
			outFile)
		if err != nil {
			log.Fatal(err)
		}
	},
}

func init() {
	opaCmd.Flags().StringVarP(&policyPath, "policy-path", "p", "", "Path to the policy")
	must(opaCmd.MarkFlagRequired("policy-path"))

	// provenanceFileURL is not required
	opaCmd.Flags().StringVarP(&provenanceFileURL, "provenance-file-url", "f", "", "Provenance file URL")

	opaCmd.Flags().StringVarP(&protectedBranch, "protected-branch", "b", "", "Protected branch")
	must(opaCmd.MarkFlagRequired("protected-branch"))

	opaCmd.Flags().StringVarP(&token, "token", "t", "", "Token")
	must(opaCmd.MarkFlagRequired("token"))

	opaCmd.Flags().StringVarP(&buildScriptPath, "build-script-path", "s", "", "Build script path")
	must(opaCmd.MarkFlagRequired("build-script-path"))

	opaCmd.Flags().StringVarP(&repositoryName, "repository-name", "r", "", "Repository name")
	must(opaCmd.MarkFlagRequired("repository-name"))

	opaCmd.Flags().StringVarP(&repositoryURL, "repository-url", "u", "", "Repository URL")
	must(opaCmd.MarkFlagRequired("repository-url"))

	opaCmd.Flags().StringVarP(&outFile, "out", "o", "", "Out")
	must(opaCmd.MarkFlagRequired("out"))

	opaCmd.Flags().BoolVarP(&debug, "debug", "d", false, "Debug")

	rootCmd.AddCommand(opaCmd)
}

func must(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
