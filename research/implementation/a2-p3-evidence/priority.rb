mine = Task.current
raise 'initial priority' unless mine.priority == 128
mine.priority = 33
raise 'get priority' unless Task.get.priority == 33
raise 'list priority' unless Task.list[0].priority == 33
