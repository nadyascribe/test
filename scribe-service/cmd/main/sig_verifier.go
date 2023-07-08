package main

import (
	"context"
	"encoding/json"
	"log"
	"os"

	"github.com/scribe-security/cocosign/attestation"
	"github.com/scribe-security/cocosign/signing/config"
	"github.com/scribe-security/cocosign/static"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

// sigVerifyCmd represents the sigVerify command
var sigVerifyCmd = &cobra.Command{
	Use:  "sig-verify",
	Args: cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		f, err := os.Open(args[0])
		if err != nil {
			log.Fatal(err)
		}

		var sig static.Signature
		if err := json.NewDecoder(f).Decode(&sig); err != nil {
			log.Fatal(err)
		}

		if err := verifySignature(&sig); err != nil {
			log.Fatal(err)
		}
	},
}

func init() {
	rootCmd.AddCommand(sigVerifyCmd)
}

func verifySignature(sig *static.Signature) error {
	l := logrus.New() // Logrus
	l.Level = logrus.DebugLevel

	cfg, err := config.DefaultSelect(config.DefaultSigstoreConfig)
	if err != nil {
		return err
	}

	att, err := attestation.NewStorerVerifierAttestation(context.Background(), cfg, l)
	if err != nil {
		return err
	}

	err = att.Verify(sig)
	if err != nil {
		return err
	}

	return nil
}
