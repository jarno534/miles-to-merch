$headers = @{
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

$assets = @(
    @{ Url = "https://files.cdn.printful.com/products/71/product_1562919362.jpg"; Dest = "d:\Miles to Merch\frontend\public\tshirt\front.jpg" },
    @{ Url = "https://files.cdn.printful.com/products/434/product_1663738096.jpg"; Dest = "d:\Miles to Merch\frontend\public\hoodie\front.jpg" },
    @{ Url = "https://files.cdn.printful.com/products/19/product_1615895744.jpg"; Dest = "d:\Miles to Merch\frontend\public\mug\center.jpg" }
)

foreach ($asset in $assets) {
    Write-Host "Downloading $($asset.Url) ..."
    try {
        Invoke-WebRequest -Uri $asset.Url -OutFile $asset.Dest -Headers $headers
        Write-Host "Success: $($asset.Dest)"
    } catch {
        Write-Host "Error downloading $($asset.Url): $_"
    }
}
