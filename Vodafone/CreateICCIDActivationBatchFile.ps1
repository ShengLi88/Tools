# Define input and output file
$inputFile = "ICCID.txt"
$outputFile = "Processed_ICCID.txt"

# Read the file and filter lines with exactly 20 characters
$validLines = Get-Content $inputFile | Where-Object { $_.Length -eq 20 }

# Append tab and 'TEST' to each valid line
$processedLines = $validLines | ForEach-Object { "$_`tTEST" }

# Count the number of lines
$lineCount = $processedLines.Count

# Define header and footer
$header = "FORMAT01`tChange Device State`tCHANGE_STATE`nICCID`tSTATE"
$footer = "END`t$lineCount"

# Write to output file
$header | Out-File -FilePath $outputFile -Encoding ASCII
$processedLines | Out-File -FilePath $outputFile -Encoding ASCII -Append
$footer | Out-File -FilePath $outputFile -Encoding ASCII -Append -NoNewline

Write-Host "Processing completed. Output saved to $outputFile"
