#!/usr/bin/env python3
"""
Swarm Pattern Generator - MiroFish-inspired glyphwork experiments

A minimal swarm simulation where agents exhibit flocking behavior
and their positions map to ASCII characters, creating emergent
typographic patterns.

Concepts from MiroFish:
- Agents as autonomous entities in a shared field
- Emergent patterns from simple local rules
- Position/density → glyph mapping for visual output

Example Output (5 frames):
```
Frame 0:
           ·                   ·        
                  ···  ····  ··         
           ·         ·   ·              
  ·       ·    ··· ·   ·· ·       ·     
               : · + ·   ·  :·          
     ·  ·  · · +  ·· ·  +·    ·         
    ·       :  ···  ·    ·: : ·         
               ·     ··                 
                 ··  ··  ·              
                                        

Frame 1:
            ·        · ·· ·             
                · ··  ·   ·  ·  ·       
             · ·  ·   ··    ·           
            ·   ··  · ·   ···     ·     
  ·   ·   ·    ·   :   ·  ·   :         
        ·     :   ·  ··    ·            
    ·     · ·  ···  · · · · · ·         
           ·      ·   ···               
                ·  · :    · ·           
      ·        · ·:    · ·   ·          

Frame 2:
                ·  · ··  ··             
           · ··   :  ·     ·:           
                  · ···:·       ·       
                :          ·  ···       
      ·    · ·     · ·   :              
   ·     ·    ·   ·    :     ·          
     ·  ·    · ·      ·  ·     ·        
      ·      ·  · ··  · ·     ·         
            ·      · ·  ·               
              · ·· ··: :  : ··          

Frame 3:
          ·   ·  ·· :··  · ·            
               ·   ·  ··  ·             
              ·      · ·   ·· ··        
        ·       · ··   ·  ·    · ·      
           ···     ·     +              
       ·      ·      · ·     ·          
       ·     · ···  ·  ·   ·   ·        
    ·  ·            ·· ·       ·        
             ··       ·   · ··          
            ·  · · ·+· :· ·             

Frame 4:
         ·    · · ·: · ··· ·            
                    ··  ·               
         ·     ·   ·    · · ··          
               ·     ·   ·    ·         
         ·  ··· ·· ·  ··  ·· ·   ·      
         ·           ···     · ·        
               ···· ·  · · · ·          
            ·        ·   ·      ·       
      · ·   · ·     ·  ·   ··           
            ·  ·· : · ··:               
```
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple


# ASCII glyphs by density (sparse → dense)
DENSITY_GLYPHS = " ·∙•●○◦◎⊙"
SIMPLE_GLYPHS = " ·:+#"


@dataclass
class Agent:
    """A single swarm agent with position and velocity."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    
    def distance_to(self, other: 'Agent') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class SwarmField:
    """
    A 2D field of swarm agents with flocking behavior.
    
    Rules:
    - Cohesion: steer toward average position of neighbors
    - Separation: avoid crowding nearby agents  
    - Alignment: steer toward average heading of neighbors
    """
    
    def __init__(
        self,
        width: int = 40,
        height: int = 10,
        num_agents: int = 75,
        perception_radius: float = 5.0,
        max_speed: float = 1.0,
        cohesion_weight: float = 0.02,
        separation_weight: float = 0.05,
        alignment_weight: float = 0.03,
        center_pull: float = 0.001,
    ):
        self.width = width
        self.height = height
        self.perception_radius = perception_radius
        self.max_speed = max_speed
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.center_pull = center_pull
        
        # Initialize agents in a loose cluster
        cx, cy = width / 2, height / 2
        self.agents: List[Agent] = []
        for _ in range(num_agents):
            x = cx + random.gauss(0, width / 6)
            y = cy + random.gauss(0, height / 4)
            vx = random.gauss(0, 0.3)
            vy = random.gauss(0, 0.3)
            self.agents.append(Agent(x, y, vx, vy))
    
    def step(self):
        """Advance simulation by one timestep."""
        # Compute new velocities based on flocking rules
        new_velocities = []
        
        for agent in self.agents:
            # Find neighbors
            neighbors = [
                other for other in self.agents
                if other is not agent and agent.distance_to(other) < self.perception_radius
            ]
            
            dvx, dvy = 0.0, 0.0
            
            if neighbors:
                # Cohesion: steer toward center of neighbors
                avg_x = sum(n.x for n in neighbors) / len(neighbors)
                avg_y = sum(n.y for n in neighbors) / len(neighbors)
                dvx += (avg_x - agent.x) * self.cohesion_weight
                dvy += (avg_y - agent.y) * self.cohesion_weight
                
                # Separation: avoid nearby agents
                for neighbor in neighbors:
                    dist = agent.distance_to(neighbor)
                    if dist > 0 and dist < self.perception_radius / 2:
                        factor = self.separation_weight / dist
                        dvx -= (neighbor.x - agent.x) * factor
                        dvy -= (neighbor.y - agent.y) * factor
                
                # Alignment: match neighbor velocity
                avg_vx = sum(n.vx for n in neighbors) / len(neighbors)
                avg_vy = sum(n.vy for n in neighbors) / len(neighbors)
                dvx += (avg_vx - agent.vx) * self.alignment_weight
                dvy += (avg_vy - agent.vy) * self.alignment_weight
            
            # Gentle pull toward center
            cx, cy = self.width / 2, self.height / 2
            dvx += (cx - agent.x) * self.center_pull
            dvy += (cy - agent.y) * self.center_pull
            
            # Update velocity
            nvx = agent.vx + dvx
            nvy = agent.vy + dvy
            
            # Limit speed
            speed = math.sqrt(nvx**2 + nvy**2)
            if speed > self.max_speed:
                nvx = nvx / speed * self.max_speed
                nvy = nvy / speed * self.max_speed
            
            new_velocities.append((nvx, nvy))
        
        # Apply velocities and update positions
        for agent, (nvx, nvy) in zip(self.agents, new_velocities):
            agent.vx = nvx
            agent.vy = nvy
            agent.x += nvx
            agent.y += nvy
            
            # Soft boundary (bounce gently)
            if agent.x < 0:
                agent.x = 0
                agent.vx *= -0.5
            if agent.x >= self.width:
                agent.x = self.width - 0.1
                agent.vx *= -0.5
            if agent.y < 0:
                agent.y = 0
                agent.vy *= -0.5
            if agent.y >= self.height:
                agent.y = self.height - 0.1
                agent.vy *= -0.5
    
    def render(self, glyphs: str = SIMPLE_GLYPHS) -> str:
        """Render current state as ASCII art."""
        # Count agents per cell
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for agent in self.agents:
            gx = int(agent.x)
            gy = int(agent.y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
                grid[gy][gx] += 1
        
        # Map counts to glyphs
        max_density = len(glyphs) - 1
        lines = []
        for row in grid:
            line = ""
            for count in row:
                idx = min(count, max_density)
                line += glyphs[idx]
            lines.append(line)
        
        return "\n".join(lines)


def run_demo(frames: int = 5, steps_per_frame: int = 3):
    """Run the swarm and print frames."""
    random.seed(42)  # Reproducible
    
    swarm = SwarmField(
        width=40,
        height=10,
        num_agents=75,
        perception_radius=6.0,
        max_speed=0.8,
        cohesion_weight=0.025,
        separation_weight=0.04,
        alignment_weight=0.02,
        center_pull=0.002,
    )
    
    print("Swarm Pattern Generator - MiroFish Glyphwork")
    print("=" * 44)
    
    for frame in range(frames):
        print(f"\nFrame {frame}:")
        print(swarm.render())
        
        # Advance simulation
        for _ in range(steps_per_frame):
            swarm.step()


def generate_sequence(frames: int = 10, **kwargs) -> List[str]:
    """Generate a sequence of frames as strings."""
    random.seed(kwargs.pop('seed', 42))
    swarm = SwarmField(**kwargs)
    
    sequence = []
    for _ in range(frames):
        sequence.append(swarm.render())
        for _ in range(3):
            swarm.step()
    
    return sequence


if __name__ == "__main__":
    run_demo()
