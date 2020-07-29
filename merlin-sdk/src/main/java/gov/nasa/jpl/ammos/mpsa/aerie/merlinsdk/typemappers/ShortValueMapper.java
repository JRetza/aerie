package gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.typemappers;

import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.activities.representation.ParameterSchema;
import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.activities.representation.SerializedValue;
import gov.nasa.jpl.ammos.mpsa.aerie.merlinsdk.utilities.Result;

public final class ShortValueMapper implements ValueMapper<Short> {
  @Override
  public ParameterSchema getValueSchema() {
    return ParameterSchema.INT;
  }

  @Override
  public Result<Short, String> deserializeValue(final SerializedValue serializedValue) {
    return serializedValue
        .asInt()
        .map(Result::<Long, String>success)
        .orElseGet(() -> Result.failure("Expected integral number, got " + serializedValue.toString()))
        .match(
            (Long x) -> {
              final var y = x.shortValue();
              if (x != y) {
                return Result.failure("Invalid parameter; value outside range of `short`");
              } else {
                return Result.success(y);
              }
            },
            Result::failure
        );
  }

  @Override
  public SerializedValue serializeValue(final Short value) {
    return SerializedValue.of(value);
  }
}
