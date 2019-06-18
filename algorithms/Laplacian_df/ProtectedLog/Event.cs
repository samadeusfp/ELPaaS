using LINQtoCSV;
using System;

namespace ProtectedLog
{
    class Event
    {

        [CsvColumn(FieldIndex = 1)]
        public string Source { get; set; }

        [CsvColumn(FieldIndex = 2)]
        public string Target { get; set; }

        [CsvColumn(FieldIndex = 3)]
        public string Relation { get; set; }

        [CsvColumn(FieldIndex = 4)]
        public DateTime Time { get; set; }
        
        public override string ToString()
        {
            return Relation + " @ " + Time;
        }
    }}
