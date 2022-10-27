package gov.nasa.jpl.aerie.merlin.server.models;

import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import gov.nasa.jpl.aerie.merlin.protocol.types.RealDynamics;
import gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue;
import gov.nasa.jpl.aerie.merlin.protocol.types.ValueSchema;
import org.apache.commons.lang3.tuple.Pair;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.stream.Collectors;

import static gov.nasa.jpl.aerie.json.Uncurry.untuple;

public record ProfileSet(
    Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<RealDynamics>>>>> realProfiles,
    Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<SerializedValue>>>>> discreteProfiles
) {
  public static ProfileSet ofNullable(
      final Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<RealDynamics>>>>> realProfiles,
      final Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<SerializedValue>>>>> discreteProfiles
  ) {
    return new ProfileSet(
        realProfiles,
        discreteProfiles
    );
  }
  public static ProfileSet of(
      final Map<String, Pair<ValueSchema, List<Pair<Duration, RealDynamics>>>> realProfiles,
      final Map<String, Pair<ValueSchema, List<Pair<Duration, SerializedValue>>>> discreteProfiles
  ) {
    return new ProfileSet(
        wrapInOptional(realProfiles),
        wrapInOptional(discreteProfiles)
    );
  }

  public static <T> Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<T>>>>> wrapInOptional(
      final Map<String, Pair<ValueSchema, List<Pair<Duration, T>>>> profileMap
  ) {
    return profileMap
      .entrySet().stream()
      .map($ -> Pair.of(
          $.getKey(),
          Pair.of(
              $.getValue().getLeft(),
              $.getValue().getRight()
               .stream()
               .map(untuple((duration, dynamics) -> Pair.of(duration, Optional.of(dynamics))))
               .toList()
          )
      ))
      .collect(Collectors.toMap(Pair::getKey, Pair::getValue));
  }

  public static <T> Map<String, Pair<ValueSchema, List<Pair<Duration, T>>>> unwrapOptional(
      final Map<String, Pair<ValueSchema, List<Pair<Duration, Optional<T>>>>> profileMap
  ) throws NoSuchElementException {
    return profileMap
        .entrySet().stream()
        .map($ -> Pair.of(
            $.getKey(),
            Pair.of(
                $.getValue().getLeft(),
                $.getValue().getRight()
                 .stream()
                 .map(untuple((duration, dynamics) -> Pair.of(duration, dynamics.get())))
                 .toList()
            )
        ))
        .collect(Collectors.toMap(Pair::getKey, Pair::getValue));
  }
}
