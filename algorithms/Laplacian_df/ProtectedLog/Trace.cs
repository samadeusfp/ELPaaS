using LINQtoCSV;
using System;

namespace ProtectedLog
{
    class Trace
    {

        [CsvColumn(FieldIndex = 1)]
        public string Sequence { get; set; }

        [CsvColumn(FieldIndex = 2)]
        public DateTime MinTimestamp { get; set; }

        [CsvColumn(FieldIndex = 3)]
        public DateTime MaxTimestamp { get; set; }

        public override string ToString()
        {
            return Sequence + " @ " + MinTimestamp + "-" + MaxTimestamp;
        }
    }}
