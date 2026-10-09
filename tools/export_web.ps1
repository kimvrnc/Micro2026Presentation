$ErrorActionPreference = 'Stop'
$base = 'C:\Users\kimve\OneDrive\Documents\00. PHD\00. CONFERENCES\2026_Micro2026\Presentation'
$pptx = Join-Path $base 'Micro2026_TakeHome_Flyer.pptx'
$out  = Join-Path $base 'web_export'
New-Item -ItemType Directory -Force -Path $out | Out-Null

Write-Host "PPTX: $pptx"
Write-Host "OUT : $out"

# Keep pictures at native resolution (no automatic downsampling)
foreach ($v in @('16.0','17.0','15.0')) {
  $k = "HKCU:\Software\Microsoft\Office\$v\PowerPoint\Options"
  try {
    New-Item -Path $k -Force | Out-Null
    Set-ItemProperty -Path $k -Name 'AutomaticPictureCompressionDefault' -Value 0 -Type DWord
    Set-ItemProperty -Path $k -Name 'ExportBitmapResolution' -Value 600 -Type DWord
    Write-Host "Set image-quality options for Office $v"
  } catch { Write-Host "skip $v" }
}

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($pptx, -1, 0, 0)   # ReadOnly, not Untitled, no Window
Write-Host ("Opened. Slides = " + $pres.Slides.Count)
Write-Host ("Slide size pt: " + $pres.PageSetup.SlideWidth + " x " + $pres.PageSetup.SlideHeight)

# A4 landscape at 600 dpi
$W = 7016
$H = 4961

for ($i = 1; $i -le $pres.Slides.Count; $i++) {
  $p = Join-Path $out ("slide{0}.png" -f $i)
  $pres.Slides.Item($i).Export($p, 'PNG', $W, $H)
  Write-Host ("Exported {0}  {1} bytes" -f $p, (Get-Item $p).Length)
}

# Vector PDF, print intent (text stays vector; images keep more detail)
$pdf = Join-Path $out 'flyer_hifi.pdf'
$pres.ExportAsFixedFormat($pdf, 2, 2)
Write-Host ("Exported {0}  {1} bytes" -f $pdf, (Get-Item $pdf).Length)

$pres.Close()
$ppt.Quit()
Write-Host "DONE_OK"
