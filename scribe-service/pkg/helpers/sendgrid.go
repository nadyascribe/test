package helpers

import (
	"time"

	"github.com/sendgrid/sendgrid-go/helpers/mail"
)

// TODO: use config? settings?

func NewAlertEmail(to, id, rule string, date time.Time) *mail.SGMailV3 {
	m := mail.NewV3Mail()
	m.SetTemplateID("d-a6b3d900063642759a8fd521a4c083ad") // TODO: get id from config/settings w/e

	address := "alerts@scribesecurity.com"
	name := "Alerts Notifications"
	e := mail.NewEmail(name, address)
	m.SetFrom(e)

	p := mail.NewPersonalization()
	tos := []*mail.Email{
		mail.NewEmail("Example User", to),
	}

	p.AddTos(tos...)

	p.SetDynamicTemplateData("alert_id", id)
	p.SetDynamicTemplateData("alert_message", rule)
	p.SetDynamicTemplateData("alert_date", date)

	m.AddPersonalizations(p)

	return m
}
