# Define the path to your JSON query file
$queryFilePath = "query.json"

# Load the content of the JSON query file
if (Test-Path $queryFilePath) {
    $content = Get-Content -Path $queryFilePath -Raw
} else {
    Write-Output "Error: The file 'query.json' was not found. Please check the path."
    exit
}

# Define the URL for the GBIF API request
$url = "https://api.gbif.org/v1/occurrence/download/request"

# Prompt for your GBIF credentials and encode them in Base64
$credential = Get-Credential -Message "Enter your GBIF username and password"
$authInfo = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes(($credential.UserName + ":" + $credential.GetNetworkCredential().Password)))

# Set headers with Authorization
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Basic $authInfo"
}

# Make the POST request to GBIF
$response = Invoke-WebRequest -Uri $url `
    -Headers $headers `
    -Method Post `
    -Body $content

# Check the response status
if ($response.StatusCode -eq 201) {
    # Extract the download key from the response body
    $downloadKey = $response.Content.Trim()
    Write-Output "Download request accepted. Download key: $downloadKey"

    # Poll for status updates until the download is ready
    $downloadStatusUrl = "https://api.gbif.org/v1/occurrence/download/$downloadKey"
    do {
        Start-Sleep -Seconds 10
        $statusResponse = Invoke-WebRequest -Uri $downloadStatusUrl -Headers $headers -Method Get
        $status = ($statusResponse.Content | ConvertFrom-Json).status
        Write-Output "Current status: $status"
    } until ($status -eq "SUCCEEDED")

    # Define the download URL for the completed download
    $downloadUrl = "https://api.gbif.org/v1/occurrence/download/request/$downloadKey.zip"

    # Download the file
    $outputFilePath = "$PWD\$downloadKey.zip"
    Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $outputFilePath
    Write-Output "Download completed. File saved as $outputFilePath"
} else {
    Write-Output "Failed to submit download request. Status code: $($response.StatusCode)"
}
