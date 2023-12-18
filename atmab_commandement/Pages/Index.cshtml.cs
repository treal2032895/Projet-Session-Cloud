using Microsoft.AspNetCore.Mvc.RazorPages;
using ScriptASPNet.Models;
using ScriptASPNet.Services;

namespace ScriptASPNet.Pages;

public class IndexPageModel : PageModel
{
    private readonly ICosmosService _cosmosService;

    public IEnumerable<Protocole>? Protocole { get; set; }

    public IndexPageModel(ICosmosService cosmosService)
    {
        _cosmosService = cosmosService;
    }

    public async Task OnGetAsync()
    {
        Protocole ??= await _cosmosService.RetrieveActiveProtocolesAsync();
    }
}