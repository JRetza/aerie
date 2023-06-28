create table metadata.activity_directive_tags(
  directive_id integer not null,
  plan_id integer not null,

  tag_id integer not null references metadata.tags
    on update cascade
    on delete cascade,

  constraint tags_on_existing_activity_directive
    foreign key (directive_id, plan_id)
      references activity_directive
      on update cascade
      on delete cascade,
  primary key (directive_id, plan_id, tag_id)
);

comment on table metadata.activity_directive_tags is e''
  'The tags associated with an activity directive.';

create function adt_check_locked_new()
  returns trigger
  security definer
  language plpgsql as $$
  begin
    call plan_locked_exception(new.plan_id);
    return new;
  end $$;
create function adt_check_locked_old()
  returns trigger
  security definer
  language plpgsql as $$
  begin
    call plan_locked_exception(old.plan_id);
    return old;
  end $$;

create trigger adt_check_plan_locked_insert_update
  before insert or update on metadata.activity_directive_tags
  for each row
  execute procedure adt_check_locked_new();
create trigger adt_check_plan_locked_update_delete
  before update or delete on metadata.activity_directive_tags
  for each row
  execute procedure adt_check_locked_old();
