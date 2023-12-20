/* --------------------------------- */
/* SCENARIOS                         */
/* --------------------------------- */

// These are JSON files containing the spatial signature and indicator values
// for each scenario.
import baseline from "src/data/scenarios/baseline.json";

// One of the scenarios is used as the 'reference', against which values are
// scaled.
const referenceScenarioObject = baseline;


// List all the other scenarios here.
const otherScenarioObjects = []