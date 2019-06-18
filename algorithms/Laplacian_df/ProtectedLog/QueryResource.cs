using Grapevine.Interfaces.Server;
using Grapevine.Server;
using Grapevine.Server.Attributes;
using Grapevine.Shared;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Linq.Expressions;
using System.Text;
using System.Threading.Tasks;

namespace ProtectedLog
{
    [RestResource]
    public class QueryResource
    {

        [RestRoute(HttpMethod = HttpMethod.GET, PathInfo = "/")]
        public IHttpContext LandingPage(IHttpContext context)
        {
            context.Response.SendResponse("<html><body>" +
                "Use query interfaces on:</br> " +
                "<a href=\"/budget\">/budget</a></br>" +
                "<a href=\"/events\">/events</a></br>" +
                "<a href=\"/traces\">/traces</a></br>" +
                "</body></html>");
            return context;
        }

        [RestRoute(HttpMethod = HttpMethod.GET, PathInfo = "/budget")]
        public IHttpContext PrivacyBudget(IHttpContext context)
        {
            context.Response.SendResponse(ProtectedLogServer.Agent.Budget.ToString());
            return context;
        }

        [RestRoute(HttpMethod = HttpMethod.GET, PathInfo = "/events")]
        public IHttpContext EventsQuery(IHttpContext context)
        {
            Double epsilon = Double.Parse(context.Request.QueryString["epsilon"] ?? "0.1", new CultureInfo("en"));
            string query = context.Request.QueryString["query"];

            try
            {
                StringBuilder response = new StringBuilder();
                response.AppendLine("Source,Target,Count");
                PINQ.PINQueryable<Event> eventQuery = ProtectedLogServer.EventQuery;
                if (query != null)
                {
                    var type = Expression.Parameter(typeof(Event), "E");
                    LambdaExpression linqQuery = System.Linq.Dynamic.DynamicExpression.ParseLambda(new[] { type }, null, query);
                    Delegate @delegate = linqQuery.Compile();
                    eventQuery = eventQuery.Where(e => (Boolean)@delegate.DynamicInvoke(e));
                }
                var parts = eventQuery.Partition(ProtectedLogServer.Relations, e => e.Relation);
                foreach (var part in parts)
                {
                    var keys = part.Key.Split(',').ToArray();
                    response.AppendLine(keys[0] + "," + keys[1] + "," + Math.Round(Math.Abs(part.Value.NoisyCount(epsilon))));
                }

                context.Response.SendResponse(response.ToString());
            }
            catch (Exception e)
            {

                if (e.Source == "PINQ")
                {
                    context.Response.StatusCode = HttpStatusCode.Forbidden;
                    context.Response.SendResponse("Privacy budget depleted");
                }
                else
                {
                    context.Response.StatusCode = HttpStatusCode.InternalServerError;
                    context.Response.SendResponse(e.Message);
                }
            }
            return context;
        }

        [RestRoute(HttpMethod = HttpMethod.GET, PathInfo = "/traces")]
        public IHttpContext TracesQuery(IHttpContext context)
        {
            Double epsilon = Double.Parse(context.Request.QueryString["epsilon"] ?? "0.1", new CultureInfo("en"));
            Int16 sequence_threshold = Int16.Parse(context.Request.QueryString["sequence_threshold"] ?? "25", new CultureInfo("en"));
            Int16 sequence_length = Int16.Parse(context.Request.QueryString["sequence_length"] ?? "10", new CultureInfo("en"));
            string query = context.Request.QueryString["query"];

            try
            {
                StringBuilder response = new StringBuilder();
                response.AppendLine("Sequence,Count");
                PINQ.PINQueryable<Trace> traceQuery = ProtectedLogServer.TraceQuery;
                if (query != null)
                {
                    var type = Expression.Parameter(typeof(Trace), "E");
                    LambdaExpression linqQuery = System.Linq.Dynamic.DynamicExpression.ParseLambda(new[] { type }, null, query);
                    Delegate @delegate = linqQuery.Compile();
                    traceQuery = traceQuery.Where(e => (Boolean)@delegate.DynamicInvoke(e));
                }
                var actIds = ProtectedLogServer.ActToId.Values.Except(new[] { ProtectedLogServer.ActToId["Start"] }).ToArray();
                string startId = ProtectedLogServer.ActToId["Start"];
                string endId = ProtectedLogServer.ActToId["End"];

                List<string> candidates = new List<string>();
                string[] wrappedStart = { startId };
                candidates.AddRange(wrappedStart.SelectMany(x => actIds.Where(a => a != endId)
                                                                       .Select(y => x + "<" + y )));

                var current_length = 2;
                while (current_length < sequence_length)
                {
                    var parts = traceQuery.Partition(candidates.ToArray(), t => string.Join("<",t.Sequence.Split('<').Take(current_length)));
                    candidates.Clear();
                    foreach (var part in parts)
                    {
                        var key = part.Key;
                        var innerQuery = part.Value;
                        var count = Math.Round(Math.Abs(innerQuery.NoisyCount(epsilon)));

                        var lastAct = key.Split('<').Last();
                        if (lastAct == endId)
                        {
                            // We have a complete trace
                            response.AppendLine(key + "," + count);
                        } else
                        {
                            if (count > sequence_threshold)
                            {

                                // Add all possible suffixes
                                string[] wrappedKey = { key};
                                var newCandidates = wrappedKey.SelectMany(x => actIds.Select(y => x + "<" + y));
                                candidates.AddRange(newCandidates);
                            }
                        }
                    }
                    current_length++;
                }
                context.Response.SendResponse(response.ToString());
            }
            catch (Exception e)
            {

                if (e.Source == "PINQ")
                {
                    context.Response.StatusCode = HttpStatusCode.Forbidden;
                    context.Response.SendResponse("Privacy budget depleted");
                }
                else
                {
                    context.Response.StatusCode = HttpStatusCode.InternalServerError;
                    context.Response.SendResponse(e.Message);
                    throw e; 
                }
            }
            return context;
        }

    }

}
