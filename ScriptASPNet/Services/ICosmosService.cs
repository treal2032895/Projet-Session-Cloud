using ScriptASPNet.Models;

namespace ScriptASPNet.Services;

public interface ICosmosService
{

    public async Task<IEnumerable<Protocole>> RetrieveActiveProtocolesAsync()
    {
        await Task.Delay(1);

        return new List<Protocole>()
        {
            new Protocole( protocole:"P01", date: DateTime.Now)     
        };
    }

    public async Task<IEnumerable<Protocole>> RetrieveAllProtocoleAsync()
    {
        await Task.Delay(1);

        return new List<Protocole>()
        {
           new Protocole( protocole:"P01", date : DateTime.Now)
        };
    }
}