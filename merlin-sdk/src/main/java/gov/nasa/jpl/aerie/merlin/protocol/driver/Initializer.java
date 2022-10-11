package gov.nasa.jpl.aerie.merlin.protocol.driver;

import gov.nasa.jpl.aerie.merlin.protocol.model.CellType;
import gov.nasa.jpl.aerie.merlin.protocol.model.OutputType;
import gov.nasa.jpl.aerie.merlin.protocol.model.Resource;
import gov.nasa.jpl.aerie.merlin.protocol.model.Task;
import gov.nasa.jpl.aerie.merlin.protocol.types.SerializedValue;
import gov.nasa.jpl.aerie.merlin.protocol.types.ValueSchema;

import java.util.function.Function;

public interface Initializer {
  <State>
  State getInitialState(CellId<State> cellId);

  <Event, Effect, State>
  CellId<State> allocate(
      State initialState,
      CellType<Effect, State> cellType,
      Function<Event, Effect> interpretation,
      Topic<Event> topic);

  void daemon(TaskFactory<?> factory);

  void resource(
      String name,
      Resource<?> resource);

  <Event>
  void topic(
      String name,
      Topic<Event> topic,
      OutputType<Event> outputType);

  interface TaskFactory<Return> {
    Task<Return> create();
  }
}
