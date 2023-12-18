using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using Timer = System.Timers.Timer;
using System.IO;
using MQTTnet;
using MQTTnet.Client;
using Microsoft.Azure.Cosmos;
using System.Collections;
using System.Configuration;
using MQTTnet.Protocol;
using System.Diagnostics.SymbolStore;
using System.Net;
using System.Net.Http;

namespace ServiceWindows
{
    public partial class Service1 : ServiceBase
    {
        private IMqttClient mqttClient;
        private Timer timer = new Timer();
       
        public Service1()
        {
            InitializeComponent();
        }

        protected async override void OnStart(string[] args)
        {
            string mqttServer = ConfigurationManager.AppSettings["MqttServer"];
            string mqttUsername = ConfigurationManager.AppSettings["MqttUsername"];
            string mqttPassword = ConfigurationManager.AppSettings["MqttPassword"];
            string mqttTopicSub = ConfigurationManager.AppSettings["MqttTopicSubscribe"];
            string mqttTopicSend = ConfigurationManager.AppSettings["MqttTopicSend"];

            WriteToFile("Service démarré à : " + DateTime.Now);

            // Créer le MQTT client
            var factory = new MqttFactory();
            mqttClient = factory.CreateMqttClient();

            //Connexion au client Mqtt
            var options = new MqttClientOptionsBuilder()
                .WithTcpServer(mqttServer)
                .WithCredentials(mqttUsername, mqttPassword)
                .Build();

            await mqttClient.ConnectAsync(options);

            //S'abonner au topic MODULE/STATUT
            var topicSubscribe = mqttTopicSub;

            await mqttClient.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic(topicSubscribe).Build());

            //Émettre sur le topic SERVICE/STATUT
            string topic = mqttTopicSend;
            var message = "Service démarré";
            var messageBuilder = new MqttApplicationMessageBuilder()
                .WithTopic(topic)
                .WithPayload(message)
                .WithQualityOfServiceLevel(MqttQualityOfServiceLevel.AtLeastOnce)
                .WithRetainFlag(false);

            await mqttClient.PublishAsync(messageBuilder.Build());

            CallAzureFunction();

            // Journaliser protocole
            string protocole = "P04";
            string topicRecept = topicSubscribe + protocole;

            mqttClient.ApplicationMessageReceivedAsync += e =>
            {
                WriteToFile(e.ApplicationMessage.Topic);
                WriteToFile($"{Encoding.UTF8.GetString(e.ApplicationMessage.Payload)}");
                protocole = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
                return Task.CompletedTask;
            };
            WriteToFile("Le protocole " + protocole + " à été complété à " + DateTime.Now);
        }

        protected async override void OnStop()
        {
            WriteToFile("Service arrêté à : " + DateTime.Now);

            string mqttTopicSub = ConfigurationManager.AppSettings["MqttTopicSubscribe"];
            string mqttTopicSend = ConfigurationManager.AppSettings["MqttTopicSend"];
            var topicSubscribe = mqttTopicSub;

            //Émettre sur le topic SERVICE/STATUT
            string topic = mqttTopicSend;
            string message = "Service arrêté";
            var messageBuilder = new MqttApplicationMessageBuilder()
                .WithTopic(topic)
                .WithPayload(message)
                //.WithQualityOfServiceLevel(MqttQualityOfServiceLevel.AtLeastOnce)
                .WithRetainFlag(false);

            await mqttClient.PublishAsync(messageBuilder.Build());

            //Déconnexion du serveur mqtt et désabonnement au topic 
            await mqttClient.UnsubscribeAsync(topicSubscribe);
            await mqttClient.DisconnectAsync();
        }

        private async Task CheckAndValidateProtocolAsync()
        {
            string mqttTopicSend = ConfigurationManager.AppSettings["MqttTopicSend"];

            while (true)
            {
                bool canLaunchProtocol = await CheckIfCanLaunchProtocolAsync();

                if (canLaunchProtocol == true)
                {
                    string mqttValidationTopic = mqttTopicSend;
                    var validationMessage = "READY";
                    var validationApplicationMessage = new MqttApplicationMessageBuilder()
                        .WithTopic(mqttValidationTopic)
                        .WithPayload(validationMessage)
                        .WithRetainFlag(false)
                        .Build();
                    await mqttClient.PublishAsync(validationApplicationMessage);
                }

                await Task.Delay(TimeSpan.FromMinutes(1)); // Wait for 1 minute before checking again
            }
        }
        private async Task<bool> CheckIfCanLaunchProtocolAsync()
        {
            string endpointUri = "https://marc-a-bouchard1.documents.azure.com:443/";
            string primaryKey = "saZq7C8cvTfvO7LKlBbtHqqceUhyUa3GJQWFI4ypY6aFrN8zrtyBN5GNL6Z6FdLj4izbiRvYBol6ACDbJY3Q0g==";
            string functionUrl = "URL_de_votre_fonction_azure"; // Remplacez cela par l'URL réelle de votre fonction Azure


            CosmosClient cosmosClient = new CosmosClient(endpointUri, primaryKey);

            Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync("CosmoBDAtmab");
            Microsoft.Azure.Cosmos.Container container = await database.CreateContainerIfNotExistsAsync("Élément", "/protocole");
            string query = "SELECT c.protocole FROM c";

            try
            {
                QueryDefinition queryDefinition = new QueryDefinition(query);
                FeedIterator<Newtonsoft.Json.Linq.JObject> queryResultSetIterator = container.GetItemQueryIterator<Newtonsoft.Json.Linq.JObject>(queryDefinition);

                while (queryResultSetIterator.HasMoreResults)
                {
                    FeedResponse<Newtonsoft.Json.Linq.JObject> currentResultSet = await queryResultSetIterator.ReadNextAsync();

                    // Parcourez les résultats de la requête pour vérifier si "P04" est renvoyé.
                    foreach (Newtonsoft.Json.Linq.JObject document in currentResultSet)
                    {
                        var protocoleValue = document["protocole"]?.ToString();
                        if (protocoleValue == "P04")
                        {
                            WriteToFile("Protocole prêt");
                            using (HttpClient client = new HttpClient())
                            {
                                HttpResponseMessage response = await client.GetAsync(functionUrl);

                                if (response.IsSuccessStatusCode)
                                {
                                    string result = await response.Content.ReadAsStringAsync();
                                    Console.WriteLine($"Réponse de la fonction Azure : {result}");
                                }
                                else
                                {
                                    Console.WriteLine($"Échec de la requête HTTP. Code d'état : {response.StatusCode}");
                                }
                            }
                            return true; // La base de données a renvoyé "P04", définissez protocoleReady à true.

                        }
                    }
                }
            }
            catch (Exception ex)
            {
                // Gérez les erreurs ici, par exemple, en enregistrant les messages d'erreur.
                WriteToFile("Erreur :" + ex);
            }
            return false; // "P04" n'a pas été trouvé dans la base de données, définissez protocoleReady à false.
        }

        static async Task CallAzureFunction()
        {
            string azureFunctionUrl = "URL_de_votre_fonction_azure";

            using (HttpClient client = new HttpClient())
            {
                HttpResponseMessage response = await client.GetAsync(azureFunctionUrl);

                if (response.IsSuccessStatusCode)
                {
                    string responseBody = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Réponse de la fonction Azure : {responseBody}");
                }
                else
                {
                    Console.WriteLine($"Échec de l'appel à la fonction Azure. Code de statut : {response.StatusCode}");
                }
            }
        }

        public void WriteToFile(string text)
        {
            string path = AppDomain.CurrentDomain.BaseDirectory + "\\Logs";
            string ext = ".txt";

            if (!Directory.Exists(path))
            {
                Directory.CreateDirectory(path);
            }

            string filePath = path + "\\ServiceLog_" + DateTime.Now.Date.ToShortDateString().Replace("/", "_") + ext;

            if (!File.Exists(filePath))
            {
                using (StreamWriter sw = File.CreateText(filePath))
                {
                    sw.WriteLine(text);
                }
            }
            else
            {
                using (StreamWriter sw = File.AppendText(filePath))
                {
                    sw .WriteLine(text);
                }
            }
        }        
    }
}
