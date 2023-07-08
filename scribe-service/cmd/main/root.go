package main

import (
	"os"

	"github.com/spf13/cobra"

	"github.com/scribe-security/scribe2/scribe-service/pkg/log"
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use: "cmd-cli",
}

func main() {
	log.Setup(true)
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}
