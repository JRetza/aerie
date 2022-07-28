create table activity (
  id integer generated always as identity,
  plan_id integer not null,

  name text,
  tags text[] default '{}',
  source_scheduling_goal_id integer,
  created_at timestamptz not null default now(),
  last_modified_at timestamptz not null default now(),
  start_offset interval not null,
  type text not null,
  arguments merlin_argument_set not null,

  constraint activity_synthetic_key
    primary key (id),
  constraint activity_owned_by_plan
    foreign key (plan_id)
    references plan
    on update cascade
    on delete cascade,
  constraint activity_start_offset_is_nonnegative
    check (start_offset >= '0')
);

create index activity_plan_id_index on activity (plan_id);


comment on table activity is e''
  'A single activity scheduled within a plan.';

comment on column activity.id is e''
  'The synthetic identifier for this activity.';
comment on column activity.plan_id is e''
  'The plan within which this activity is scheduled.';
comment on column activity.name is e''
  'The name of this activity.';
comment on column activity.tags is e''
  'The tags associated with this activity.';
comment on column activity.source_scheduling_goal_id is e''
  'The scheduling goal that this activity was generated by.';
comment on column activity.created_at is e''
  'The time at which this activity was created.';
comment on column activity.last_modified_at is e''
  'The time at which this activity was last modified.';
comment on column activity.start_offset is e''
  'The non-negative time offset from the start of the plan at which this activity is scheduled.';
comment on column activity.type is e''
  'The type of the activity, as defined in the mission model associated with the plan.';
comment on column activity.arguments is e''
  'The set of arguments to this activity, corresponding to the parameters of the associated activity type.';


create function increment_revision_on_insert_activity()
returns trigger
security definer
language plpgsql as $$begin
  update plan
  set revision = revision + 1
  where id = new.plan_id;

  return new;
end$$;

create trigger increment_revision_on_insert_activity_trigger
after insert on activity
for each row
execute function increment_revision_on_insert_activity();

create function increment_revision_on_update_activity()
returns trigger
security definer
language plpgsql as $$begin
  update plan
  set revision = revision + 1
  where id = new.plan_id
    or id = old.plan_id;

  return new;
end$$;

create trigger increment_revision_on_update_activity_trigger
after update on activity
for each row
execute function increment_revision_on_update_activity();

create function increment_revision_on_delete_activity()
returns trigger
security definer
language plpgsql as $$begin
  update plan
  set revision = revision + 1
  where id = old.plan_id;

  return old;
end$$;

create trigger increment_revision_on_delete_activity_trigger
after delete on activity
for each row
execute function increment_revision_on_delete_activity();

create or replace function generate_activity_name()
returns trigger
security definer
language plpgsql as $$begin
  new.name = new.type || ' ' || new.id;
  return new;
end$$;

comment on function generate_activity_name() is e''
  'Generates a name for an activity as the activity type + activity id.';

create trigger generate_name_trigger
before insert on activity
for each row execute function generate_activity_name();

comment on trigger generate_name_trigger on activity is e''
  'Generates a name for an activity as the activity type + number from sequence of the type scoped to its plan.';

create or replace function activity_set_updated_at()
  returns trigger
  security definer
  language plpgsql as $$begin
  new.last_modified_at = now();
  return new;
end$$;

comment on function activity_set_updated_at() is e''
  'Sets the last_modified_at field of an activity to the current time.';

create trigger set_timestamp
  before update on activity
  for each row
execute function activity_set_updated_at();

comment on trigger set_timestamp on activity is e''
  'Sets the last_modified_at field of an activity to the current time.';
