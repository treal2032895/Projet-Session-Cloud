using ScriptASPNet.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();

builder.Services.Configure<RouteOptions>(o =>
{
    o.LowercaseUrls = true;
    o.LowercaseQueryStrings = true;
});
builder.Services.AddScoped<CosmosService>();
builder.Services.AddSingleton<ICosmosService, CosmosService>();

var app = builder.Build();

app.UseRouting();

app.MapRazorPages();

app.UseStaticFiles();

app.Run();