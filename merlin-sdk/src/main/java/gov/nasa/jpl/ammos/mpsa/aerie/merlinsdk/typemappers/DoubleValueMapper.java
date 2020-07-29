package gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.typemappers;

import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.activities.representation.ParameterSchema;
import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.activities.representation.SerializedValue;
import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.utilities.Result;

public final class DoubleValueMapper implements ValueMapper<Double> {
  @Override
  public ParameterSchema getValueSchema() {
    return ParameterSchema.REAL;
  }

  @Override
  public Result<Double, String> deserializeValue(final SerializedValue serializedValue) {
    return serializedValue
        .asReal()
        .map(Result::<Double, String>success)
        .orElseGet(() -> Result.failure("Expected real number, got " + serializedValue.toString()));
  }

  @Override
  public SerializedValue serializeValue(final Double value) {
    return SerializedValue.of(value);
  }
}
