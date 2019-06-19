using PINQ;

namespace ProtectedLog
{
    partial class ProtectedLogServer
    {
        public class PINQAgentObservableBudget : PINQAgent
        {

            public double Budget { get; private set; }

            /// <summary>
            /// Tests if the increment epsilon is acceptable. If so, the budget is decremented byfore returning.
            /// </summary>
            /// <param name="epsilon">epsilon</param>
            /// <returns>True iff the remain budget supports the decrement.</returns>
            public override bool apply(double epsilon)
            {
                if (epsilon > Budget)
                    return false;

                Budget -= epsilon;
                return true;
            }
            /// <summary>
            /// Constructor for a PINQAgentBudget
            /// </summary>
            /// <param name="b">The initial budget setting.</param>
            public PINQAgentObservableBudget(double b)
            {
                Budget = b;
            }
        }
    }
}
