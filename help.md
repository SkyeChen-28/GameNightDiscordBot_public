# Commands

---

```sh
/imposter 
```
Selects n people to assign the `imposter-name` role to. Then, privately DMs everyone their role. Optionally remove selected imposters from future candidate pools.
*Optional Arguments:*
- `imposter-name`: The name of the imposter role. Default = "Imposter"
- `safe-role-name`: The name of the non-imposter role. Default = "NOT Imposter"
- `n`: The number of people to select as the imposter role. Default = 1
- `remove-from-candidate-pool`: Removes selected imposters from future candidate pools. Default = False
- `imposter-knowledge`: Determines whether imposters are aware of each other's roles. Default = True

---

```sh
/select 
```
Selects n people to assign the `role-name` role to. Then, publicly posts who has the role. Optionally remove them from future candidate pools.
*Optional Arguments:*
- `role-name`: The name of the selected role. Default = "Superstar"
- `n`: The number of people to select for the role. Default = 1
- `remove-from-candidate-pool`: Removes selected people from future candidate pools. Default = False
