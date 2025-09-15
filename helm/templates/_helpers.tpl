{{- define "aiops-api.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{- define "aiops-api.fullname" -}}
{{ include "aiops-api.name" . }}
{{- end -}}