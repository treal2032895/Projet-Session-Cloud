using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using ScriptASPNet.Models;
using Microsoft.Azure.Cosmos;
using Microsoft.Azure.Cosmos.Linq;
using System.ComponentModel;
using ScriptASPNet.Services;

namespace ScriptASPNet.Pages
{
    public class AjoutP04Model : PageModel
    {

        private CosmosService _cosmosService;

        public AjoutP04Model(ICosmosService cosmosService)
        {
          
            _cosmosService = new CosmosService();

            Protocole newProtocole = new Protocole
            (
                protocole : "P04",
                DateTime.Now
            );

            EnvoiAsync(newProtocole);
        }

        private async Task EnvoiAsync(Protocole newProtocole)
        {
            await _cosmosService.container.UpsertItemAsync<Protocole>(item: newProtocole);
        }
    }
}
