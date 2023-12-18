using ScriptASPNet.Models;
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;
using System.ComponentModel;

namespace ScriptASPNet.Services
{
    
    public class CosmosService : ICosmosService
    {
        private static bool siValide = false;
        private readonly CosmosClient _client;
        public CosmosService()
        {
            _client = new CosmosClient(
              connectionString: "AccountEndpoint=https://marc-a-bouchard1.documents.azure.com:443/;AccountKey=saZq7C8cvTfvO7LKlBbtHqqceUhyUa3GJQWFI4ypY6aFrN8zrtyBN5GNL6Z6FdLj4izbiRvYBol6ACDbJY3Q0g==;");
        }
        public Microsoft.Azure.Cosmos.Container container
        {
            get => _client.GetDatabase("CosmoBDAtmab").GetContainer("�l�ment");
        }

        public async Task<IEnumerable<Protocole>> RetrieveAllProtocoleAsync()
        {
            var queryable = container.GetItemLinqQueryable<Protocole>();
            using FeedIterator<Protocole> feed = queryable
            .Where(p => p.protocole == "P01")
            .ToFeedIterator();

            List<Protocole> results = new();

            while (feed.HasMoreResults)
            {
                var response = await feed.ReadNextAsync();
                foreach (Protocole item in response)
                {
                    results.Add(item);
                }
            }
            return results;
        }

        public async Task<IEnumerable<Protocole>> RetrieveActiveProtocolesAsync()
        {
            string sql = @"
    SELECT
        p.protocole,
        p.date
    FROM Items p
";

            var query = new QueryDefinition(sql);

            using var feed = container.GetItemQueryIterator<Protocole>(query);

            List<Protocole> results = new();
            DateTime currentDate = DateTime.Now;

            bool p01Success = false;
            bool p02Success = false;
            bool p03Success = false;

            while (feed.HasMoreResults)
            {
                FeedResponse<Protocole> response = await feed.ReadNextAsync();

                foreach (Protocole item in response)
                {
                    results.Add(item);

                    if (item.protocole == "P01" || item.protocole == "P02" || item.protocole == "P03")
                    {
                        // V�rifie si la diff�rence entre la date du protocole et la date actuelle est inf�rieure � une heure
                        bool isProtocolInLastHour = (currentDate - item.date).TotalHours < 1;

                        // Si le protocole est dans la derni�re heure
                        if (isProtocolInLastHour)
                        {
                            if (item.protocole == "P01")
                            {
                                p01Success = true;
                            }
                            else if (item.protocole == "P02")
                            {
                                p02Success = true;
                            }
                            else if (item.protocole == "P03")
                            {
                                p03Success = true;
                            }
                        }
                    }
                }
            }

            // V�rifie si les trois protocoles ont �t� r�ussis dans la derni�re heure
            if (p01Success && p02Success && p03Success)
            {
                // Si les trois protocoles ont �t� r�ussis, active siValide et appelle ShowLaunch
                siValide = true;
                await ShowLaunch();
                Console.WriteLine("ShowLaunch appel�e.");
            }
            else
            {
                siValide = false;
            }

            return results;
        }

        private bool CheckProtocolSuccess(string protocol, DateTime startTime)
        {
            return true;
        }
        public async Task<bool> ShowLaunch()
        {
            Console.WriteLine($"ShowLaunch appel�e, retourne {siValide}");
            return siValide;
        }
        public async Task AddNewProtocolToDatabase(string newProtocol)
        {
            Protocole newProtocole = new Protocole
            (
                newProtocol,
                DateTime.Now
            );
            // Utilisez le SDK Cosmos DB pour ins�rer le nouveau protocole dans la base de donn�es
            try
            {
                ItemResponse<Protocole> response = await container.CreateItemAsync(newProtocole);

                if (response.StatusCode == System.Net.HttpStatusCode.Created)
                {
                    Console.WriteLine($"Successfully added new protocol {newProtocol} to the database.");
                }
                else
                {
                    Console.WriteLine($"Failed to add new protocol {newProtocol} to the database. Status code: {response.StatusCode}");
                    // G�rez l'�chec en cons�quence
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while adding new protocol {newProtocol} to the database: {ex.Message}");
                // G�rez l'exception en cons�quence
            }
        }
    }
    
}