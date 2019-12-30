# Objective

The objective of this piece of documentation is to document the perfect snake possible by considering the perfect snake AI. It is to be used as a model for The Machine snake.

# Limitations

Some of the requirements of a perfect snake could be items that would be too computationally hard algorithms. As such, possible heuristics shall be described in this documentation as well if known.

# Contents

We'll start off by talking about the ideal snake in a single-player setting. Afterwards, we'll move on to the details of a multiplayer snake. The multiplayer snake will be broken down into multiple strategies that have the potential of being an ideal. We'll also have a section regarding misc. problems that are important to discuss alone.

# Singleplayer Snake

In such a setting, the ideal is dependent on one's definition. For our purposes, we'll describe it as a snake that is able to survive the maximum number of turns possible. Intuitively, this tells us that the snake should not go for food unless it needs it and instead it should just move around the board safely. So we'll break this section down into 2 phases: the phase when it's using up it's health and moving around the board, and the second stage is when it's almost about to die so it run towards the food. Afterwards, we'll talk about another potential strategy that treats it as only one phase: Just a very long route to a food.

## Strategy #1: Two Individual Phases w/ Tail Chasing

The requirements for this stage are that the snake needs to be moving around safely and it needs to be moving around in such a way so as to ensure that when the time is right (it's almost about to starve out), it'll be ready to eat a food. If we move around the board chasing our tail, we'll be moving around safely. That's one requirement fulfilled. The next requirement is to make sure that it goes for food as we want it to as it was described above. This requirement can be fulfilled by using A* algorithms to make sure that we can still get food after we make our tail move. Although the use of A* becomes questionable here because A* is going to give you the shortest path to the food, which may not gurantee survival of the snake.

### The Problem with Using A*

But also, just because you're going to die after getting the food by using the shortest path to the food doesn't necessarily mean that that food is bad. Indeed, it could be that after using a longer path to that food, the snake will live. Indeed, this stems from one of the bigger problems with A* with using it's base implementation. Not every path is made equal, even if it may seem so. Costs are hard to assign because it's hard to say which move will turn out being the best. An important check we should think of implementing with A* is to make sure certain death can not be guranteed for our snake. If it can be, then we should not except that path and look at other potential paths. Although to accomplish this specific need, we would need to modify the A* algorithm to make sure that when after reaching it's food.

**Solution: Modify A\* algorithm so routes that will end up guranteeing death are ignored. Possible caveat: maybe using djisktra will be better since manhattan distance could slow down pathfinding using A\*?**

So to continue on with our phase 1 analysis, so far we'll have a snake that'll be able to move around the board chasing it's tail, and when it's time, it'll use a modified A* (or djiksta's) algorithm that doesn't gurantee that a shortest path will be used, but it gurantees the shortest possible route that won't kill the snake will be used. Everytime it's about to go chase it's tail, it checks to make sure that it'll be able to get the food after it makes its tail move. If it can, then it just continues following it's tail. If it can't then it'll go for the food. However, there's another question we face. Should the A* algorithm account for the health of our snake? This is a tricky question actually.

### Should Our Modified A* (or Djisktra's) Algorithm Care About Our Snake's Limited Health?

On one hand, good arguments for make the modified algorithm care about the health is that this could speed up our algorithm: If the length of the path is greater than our health and we haven't come across any foods yet, then we can just not search that path because it's a path that we could never take anyway. Only potential downside I could see for this is if we wouldn't want to do this in some situations which I can't predict right now. Regardless, a solution could be to have multiple pathfinding algorithms and use this described pathfinding algorithm only for needed cases.

We are almost at the end of our analysis, but one final point is: what should the snake be doing at the start of the game? It can't chase it's own tail because it's still growing out.

### Starting Move

I think the answer here is simply that there's more than one answer. You could just make a single random move anywhere that's not going to kill you and then in the next move, you could go to your tail safely. Truly the start of the game is a wacky situation that's really not easy to think about in the general context of the rest of the game. It is a case that needs to be considered on its own.

Finally, we are done with our strategy #1 analysis. All that is needed is a modified A* or djikstras pathfinding algorithm that'll think about whether a path will end up killing us (and ignore that path and look into other paths) and also to account for the health of our snake and to not look at paths that are going to kill us because of health starvation. This coupled with "A Gurantee of Death Algorithm" should make this strategy possible for a perfect single player game.

### Problems So Far

From my testing, I've found that while my logic stated throughout this strategy is logically sound, the time requirements to accomplish what I want are too great. We can come up with dirty heuristics to mock the behaviour described, and it would work well probably, but instead I will direct my attention to multiplayer strategies.

## Strategy #2: A Single, Long Food-Targeted Path

In this strategy, the idea is basically that our move everytime will be just a very long path to an existing food. The lenght of this path will either be equal to our health or equal to our health - 1 (this is because it is sometimes impossible to get food in even moves). While this strategy may seem appealing because of it's simplicity, I can envision there being some problems such as node avoidal due to other foods, time complexity issues, etc. Strategy #1 seems like a viable option which is why I will leave this option documented, yet not expanded. If for some reason strategy #1 doesn't work out, this can be expanded later.

# Multiplayer Snake

## Strategy #1: Safe Snake + Samaritan Big Boi Strategy

I want to try a new strategy where I implement two different strategies (or maybe even 3 different strategies, it would depend on what the testing results say) when playing with other people. When playing against 2 or more enemy snakes, I want to minimize my length and stay as safe as possible, making sure I only eat food when I really need to (Safe Snake Strategy). When two other snakes are left, I'll still try to stay safe but get safe food when I can. When only a 1v1 is left, a different strategy will be implemented where I try to be bigger than the enemy, start to prioritize food, and try some attacking strategies including trying to starve out the enemy (Samaritan Strategy).

### Small Snake Strategy

I want to stay as safe as possible so I will get the cost of all my neighbouring nodes and go to the nodes which have the leasts cost.

### Samaritan Strategy

Prioritize cornering, trapping, or walling enemies if possible.
If snake's health is low,
    go for safe/risky food,
    else if you're the biggest snake then attack the enemy snake.
    else chase your tail.
Else if snake is not the biggest,
    go for safe/risky food,
    if you can't, chase tail
Else we don't need food and we are the biggest, so
    go for safe food
    attack
    go to tail
    get risky food
If no objective so far,
    stall
If still no objective,
    die
If after making the move, I can be killed, then find another move.
If no other moves can be found, then use floodfill to go to a place with most space.

# Misc. Problems

## Modified A* Algorithm (BattleStar)

This is the most important problem we need to solve currently. First I will have to talk about the reasons we can't use our a normal A* algorithm, and what our BattleStar algorithm will need to do.

### Why Can't We Use a Regular A* Algorithm?

This is because a normal A* algorithm assumes that a node's neighbours will stay the same no matter what. Because of this, as soon as we expand on a node, we make sure we can't expand on it in the future. This is because if we've expanded on a node, then it is unquestionably true that there is no lower cost way to get to that node. While this is true, the fact still remains that in battlesnake, it may be better for us to revisit this node again in case our neighbours change. This can happen because the "walls" or the snake's bodies are constantly changing and moving. Because of this, A* in its current form can't work for us. We need to be able to revisit nodes again.

Now that we've talked about why normal A* won't work. We need to talk about what differences/changes need to be made to the A* algorithm to make it suitable for Battlesnake. Here's a list of things BattleStar needs to be able to do on top of the current A* stuff:

* Be able to revisit nodes in the future.
* Build new boards for every path moves that are made using A*. This will allow us to:
    * If our snake's health is 0. Then terminate the path as we can't use it. This is regardless of if we've made it to the target or not because if we've reached our target but we are out of health, then we are dead and we ideally don't want that. If in fact we do want this for any reason, then this requirement can be revisited.
    * Get valid neighbouring nodess for a specific path. To elaborate on this, let's talk about what used to happen when I called get_neighbours for a specific node. It might have given us neighbour nodes that we've already traversed on our path. While this may not have been an issue since we were using a set to ignore any nodes that we've already traversed, it would be a problem now because we want to allow our algorithm to be able to revisit nodes. However, if we keep a board for every move we do and then get neighbours, then it won't give us nodes as neighbours that we've already traversed since they would be invalid neighbours.
* Make sure that the time complexity is as small as possible.

It should be noted that we face a question when we start thinking about enemy snakes in the context of building a new board. If we are building new boards with the moves that our snake might make using the BattleStar algorithm, how are we to know what moves enemies are going to make? How are we supposed to make moves for them? This is a question with no easy answer. This line of thought will have to be expanded on when we go into making a multiplayer snake but for right now, this will work well for our singleplayer snake.

### Problems I've ran into so far

* If the minimum distance to the target node is still going to kill me, then BattleStar will try to search through every single possible path on the board to find a path to that target node. Even though it doesn't exist. We need to add more checks to make sure that it doesn't search through every single path possible. I've currently added a test in the algorithm to make sure that it checks that if the manhattan distance is greater than my snake's health, then to return None.
* Second optimization is that if my manhattan distance from a path to target is less than my health, then ignore that route that I'm taking.

### Results so Far

From my testing, this current implementation of BattleStar is way too slow. It's slow because it's calculating all possible paths to a destination. This is not always so bad, but it can be if the target is far enough away from the start node. No optimizations I'm adding are improving the runtime enough to warrant the use of this algorithm. The conclusion is that considering all possible paths is implausible unless we know the destination and target are close together. This algorithm could still serve to be useful in certain situations, but those situations would have to be properly identified. For example, you can't use BattleStar to get food that's on the other side of the board. However, you can use it if you are stuck and you need to get out. In conclusion, BattleStar should stay implemented, but it should only be considered using if we are stuck. At least for the time being.

The only possible way I can see this algorithm working is if I can implement D* lite and then build battlestar on top of that. Maybe with the memory storing capabilities of D* lite, it'll help make this work in some cases.

I have some more thoughts on this. It seems in some scenarios, it could be important to use this algorithm. For example, if there's a food that we can't get to (unlikely scenario), or if we are trapped somewhere (much much more likely), or if we are following someone's tail, then it may make sense to use this type of algorithm.

## A Gurantee of Death Algorithm

In my time playing battlesnake, I have only come up with heuristics as to check whether our snake is guranteed to die. Some of these heuristics worked well in some cases, but worked terribly in others. It definitely seems like a gurantee of death algorithm is one that is important to the functioning of a good snake.

So what gurantees that a snake will die? In singleplayer games, this is easier to tell but there are some factors to consider. But first let's ask ourselves, what does it mean to say that death for a snake is guranteed?

### What Does It Mean To Say That Death is Guranteed?

To ask this question is to ask whether there's a limited number of moves available to a snake such that for any combination of those moves results in the snake dying through collision with a snake's body, with a wall or death by starvation.

### Death by Starvation

This seems like a trivial enough check. If the length of the shortest path to the closest food is greater than our remaining health, then we are dead. So this case will not be considered in the next few ideas since we can just use this idea as a check. This would be our trivial check.

### Idea #1: Plot longest path to the best escape route (our disapearing body)

**ASSUMPITON: If we aren't about to starve, then the only possible way we are GURANTEED to die is if have blocked ourselves off.** Then the solution is to escape this trap we have created for ourselves. The best way to do this is to find the longest path to our own body that's closest to our tail and that's reachable through BFS. If such a path exists, then we will need to ensure that the length of our path + any foods that are on the path is less than the time to disappear for that node of our body that we have selected. If this is the case, then we can get out easily.

## How To Detect If We Are Trapped

BFS to tail and if it is reachable, then we aren't trapped, else, we are trapped. This idea is questionable however.

## Least Dense Region

How to know which region is least dense? BFS from every snake's head to every node. For every iteration of BFS, assign a value of (number of iterations * x) to the node where x is 1 if the snake is smaller than us and 2 otherwise. Then go through this map we've created and for the node that has the greatest value, return that node.