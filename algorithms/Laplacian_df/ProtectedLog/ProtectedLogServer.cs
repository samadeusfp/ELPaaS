using Grapevine.Server;
using LINQtoCSV;
using PINQ;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace ProtectedLog
{
    partial class ProtectedLogServer
    {

        public static PINQAgentObservableBudget Agent { get; private set; }

        public static PINQueryable<Event> EventQuery { get; private set; }
        public static PINQueryable<Trace> TraceQuery { get; private set; }

        public static string[] Relations { get; private set; }        
        public static Dictionary<string, string> ActToId { get; private set; }
        public static Dictionary<string, string> IdToAct { get; private set; }
        

        private static CsvContext cc = new CsvContext();              
        private static CsvFileDescription inputFileDescription = new CsvFileDescription
        {
            SeparatorChar = ',',
            FirstLineHasColumnNames = true            
        };


        static void Main(string[] args)
        {

            if (args.Length != 4)
            {
                Console.WriteLine("Missing parameters ...");
                Console.WriteLine("Usage: ProtectedLog.exe activityFile precedenceFile sequenceFile privacyBudget");
                Console.WriteLine("Example: ProtectedLog.exe log-activities.csv log-precedence.csv log-sequences.csv 10.0");
                Console.ReadKey();
                return;
            }

            var activityFile = args[0];
            var precedenceFile = args[1];
            var sequenceFile = args[2];
            var privacyBudget = Double.Parse(args[3], new CultureInfo("en"));

            Agent = new PINQAgentObservableBudget(privacyBudget);
            
            ActToId = cc.Read<ActivityEntry>(activityFile, inputFileDescription).ToDictionary(a => a.Activity, a => a.Id);
            IdToAct = cc.Read<ActivityEntry>(activityFile, inputFileDescription).ToDictionary(a => a.Id, a => a.Activity);
            var activities = ActToId.Select(a => a.Key).ToArray();
            Relations = activities.SelectMany(x => activities.Select(y => x + "," + y)).ToArray();
            wrapPrecedenceTable(precedenceFile);
            wrapSequenceTable(sequenceFile);

            /**** Data is now sealed up. Use from this point on is unrestricted ****/
            
            using (var server = new RestServer())
            {
                server.LogToConsole().Start();
                Console.ReadLine();
                server.Stop();
            }

        }

        private static void wrapPrecedenceTable(string precedenceFile)
        {
            IEnumerable<Event> events = cc.Read<Event>(precedenceFile, inputFileDescription);
            EventQuery = new PINQueryable<Event>(events.AsQueryable(), Agent);
        }

        private static void wrapSequenceTable(string sequenceFile)
        {
            IEnumerable<Trace> traces = cc.Read<Trace>(sequenceFile, inputFileDescription);
            TraceQuery = new PINQueryable<Trace>(traces.AsQueryable(), Agent);
        }

        private static void dumpObject<T>(IEnumerable<T> obj)
        {
            foreach (var enumerable in obj)
            {
                Console.WriteLine(enumerable);
            }
        }
    }
}
