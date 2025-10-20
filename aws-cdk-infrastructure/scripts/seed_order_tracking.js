import {
  DynamoDBClient,
  BatchWriteItemCommand,
} from "@aws-sdk/client-dynamodb";
import { marshall } from "@aws-sdk/util-dynamodb";

const client = new DynamoDBClient({ region: "us-east-1" });

function generateTrackingData(n = 10) {
  const carriers = ["FedEx", "UPS", "DHL", "USPS"];
  const statuses = [
    "In Transit",
    "Delivered",
    "Delayed",
    "Out for Delivery",
    "Exception",
  ];
  const locations = [
    "Distribution Center, New York, NY",
    "Sorting Facility, Los Angeles, CA",
    "Warehouse, Dallas, TX",
    "On Truck, Chicago, IL",
  ];

  const data = [
    {
      tracking_number: "TRK123456789",
      orderId: 2324,
      status: "In Transit",
      last_update: "2025-09-01T15:00:00Z",
      estimated_delivery: "2025-09-08",
      days_in_transit: 6,
      carrier: "FedEx",
      location: "Distribution Center, New York, NY",
    },
    {
      tracking_number: "3521",
      orderId: 4521,
      status: "Delivered",
      last_update: "2025-09-07T12:00:00Z",
      estimated_delivery: "2025-09-06",
      days_in_transit: 7,
      carrier: "UPS",
      location: "Customer Address, Boston, MA",
    },
  ];

  // Add more random records
  for (let i = data.length; i < n; i++) {
    const now = new Date();
    const pastDate = new Date(now);
    pastDate.setDate(now.getDate() - Math.floor(Math.random() * 3));

    const futureDate = new Date(now);
    futureDate.setDate(now.getDate() + Math.floor(Math.random() * 5) + 1);

    data.push({
      tracking_number: `TRK${i + 1000}`,
      orderId: 3000 + i,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      last_update: pastDate.toISOString(),
      estimated_delivery: futureDate.toISOString().split("T")[0],
      days_in_transit: Math.floor(Math.random() * 10) + 1,
      carrier: carriers[Math.floor(Math.random() * carriers.length)],
      location: locations[Math.floor(Math.random() * locations.length)],
    });
  }

  return data;
}

async function seedData() {
  const items = generateTrackingData(10);

  // DynamoDB allows 25 items per batch write
  const batches = [];
  for (let i = 0; i < items.length; i += 25) {
    batches.push(items.slice(i, i + 25));
  }

  for (const batch of batches) {
    const params = {
      RequestItems: {
        OrderTrackingInfo: batch.map((item) => ({
          PutRequest: { Item: marshall(item) },
        })),
      },
    };

    await client.send(new BatchWriteItemCommand(params));
    console.log(`Inserted batch of ${batch.length} items`);
  }

  console.log(
    `Inserted ${items.length} dummy tracking records into OrderTrackingInfo`
  );
}

seedData().catch((err) => {
  console.error("Error inserting data:", err);
});
