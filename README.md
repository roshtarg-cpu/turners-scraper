# Turners.co.nz Car Scraper

Extract car listings from Turners.co.nz, New Zealand's largest used car network with nearly 3,000 vehicles across 20+ locations nationwide.

## What is Turners.co.nz?

Turners is New Zealand's most trusted used vehicle dealership, selling over 1 million cars since 1960. They operate 20+ branches from Whangarei to Invercargill, offering cars, trucks, motorcycles, boats, and general goods.

## Features

- ✅ **Comprehensive Data**: Extracts price, year, make, model, odometer, transmission, fuel type, color, location, and images
- 🔍 **Smart Filtering**: Filter by location, make, model, price range, year range, and color
- 🌏 **Nationwide Coverage**: Access inventory from all 20+ Turners branches across New Zealand
- 🚀 **Fast & Reliable**: Lightweight HTTP scraping with automatic retry logic
- 🤖 **AI Agent Ready**: Works seamlessly with Claude, ChatGPT, and other AI agents via Apify MCP

## Use Cases

- **Market Research**: Analyze used car pricing trends in New Zealand
- **Price Comparison**: Compare prices across makes, models, and locations
- **Inventory Tracking**: Monitor Turners' stock levels and turnover
- **Automotive Data**: Build datasets for ML, analytics, or business intelligence
- **AI Assistants**: Power chatbots and virtual assistants with real-time car data

## Input

```json
{
  "maxResults": 50,
  "location": "Auckland",
  "make": "Toyota",
  "model": "Camry",
  "priceMin": 10000,
  "priceMax": 30000,
  "yearMin": 2015,
  "yearMax": 2023,
  "color": "White"
}
```

### Input Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `maxResults` | integer | Maximum results to scrape (default: 50) | `100` |
| `location` | string | Branch location filter | `"Auckland"`, `"Wellington"`, `"Christchurch"` |
| `make` | string | Car manufacturer | `"Toyota"`, `"Mazda"`, `"Honda"` |
| `model` | string | Car model | `"Corolla"`, `"CX-5"`, `"Civic"` |
| `priceMin` | integer | Minimum price in NZD | `5000` |
| `priceMax` | integer | Maximum price in NZD | `50000` |
| `yearMin` | integer | Minimum year | `2010` |
| `yearMax` | integer | Maximum year | `2024` |
| `color` | string | Color preference | `"White"`, `"Black"`, `"Silver"` |
| `proxyConfiguration` | object | Apify proxy settings | See Apify docs |

## Output

```json
{
  "url": "https://www.turners.co.nz/Cars/Used-Cars-for-Sale/toyota/camry/28123456",
  "title": "2018 Toyota Camry",
  "year": "2018",
  "make": "Toyota",
  "model": "Camry",
  "price": "24,990",
  "location": "Auckland - Westgate",
  "odometer": "65,432 km",
  "transmission": "Automatic",
  "fuelType": "Petrol",
  "engine": "2,494 cc",
  "color": "White",
  "bodyStyle": "Sedan",
  "driveType": "Front Wheel Drive",
  "seats": "5",
  "description": "One owner, full service history...",
  "images": [
    "https://content.tgstatic.co.nz/...",
    "https://content.tgstatic.co.nz/..."
  ],
  "scrapedAt": "2026-09-10T12:34:56.789Z"
}
```

## How It Works

1. Navigates to Turners.co.nz search results
2. Extracts car listing URLs from search pages
3. Visits each car detail page
4. Extracts specifications, pricing, and images
5. Applies your filters (price, year, make, model)
6. Returns structured JSON data

## For AI Agents (Claude, ChatGPT, MCP)

This actor is optimized for AI agent workflows via Apify's Model Context Protocol (MCP) integration:

```javascript
// Example MCP usage with Claude
const listings = await apify.call('fervent_bus/turners-scraper', {
  maxResults: 20,
  make: 'Toyota',
  location: 'Auckland'
});
```

Perfect for:
- Building car recommendation chatbots
- Powering voice assistants with NZ car data
- Automating market research reports
- Creating price alert systems

## Performance

- **Speed**: ~2-5 seconds per car listing
- **Capacity**: Can handle 1,000+ cars per run
- **Reliability**: Automatic retry on failures
- **Cost**: ~$0.005 per car + $0.05 per run

## Locations Covered

Turners operates across 20+ branches in New Zealand:

**North Island**: Whangarei, North Shore, Westgate, Botany, Manukau, Penrose, Avalon Drive, Te Rapa, Mount Maunganui, Rotorua, Napier, New Plymouth, Palmerston North, Wellington (Porirua)

**South Island**: Nelson, Wairakei Rd (Christchurch), Hornby, Moorhouse Ave (Christchurch), Timaru, Dunedin, Invercargill

## Tags

`cars`, `new-zealand`, `automotive`, `used-cars`, `turners`, `vehicles`, `market-data`, `ai-agents`, `mcp`, `claude`, `chatgpt`

## Support

For issues or questions, please contact the actor maintainer or file an issue on GitHub.

## License

This actor is for data extraction purposes only. Please respect Turners.co.nz's terms of service and robots.txt. Use responsibly and ethically.
