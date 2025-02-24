<script>
  import { onMount } from 'svelte';

  let ladder = [];
  let clues = [];
  let revealedWords = [];
  let currentInput = '';
  let gameComplete = false;
  let errorMessage = '';
  
  onMount(async () => {
    try {
      const response = await fetch('/data/puzzle.txt');
      const text = await response.text();
      
      // Split the text into lines and process in pairs
      const lines = text.trim().split('\n');
      const ladderData = [];
      
      // Process lines in pairs (word + transformation)
      for (let i = 0; i < lines.length; i += 2) {
        const word = lines[i].trim();
        const transformation = i + 1 < lines.length ? lines[i + 1].trim() : null;
        
        ladderData.push({
          word: word,
          transformation: transformation
        });
      }
      
      // Process the ladder data
      ladder = ladderData.map((node, index) => ({
        word: node.word,
        transformation: node.transformation,
        isRevealed: index === 0 || index === ladderData.length - 1
      }));
      
      // Create alphabetically sorted clues
      clues = ladderData
        .filter(node => node.transformation)
        .map(node => ({
          text: node.transformation,
          isUsed: false
        }))
        .sort((a, b) => a.text.localeCompare(b.text));
      
      // Initialize revealed words with first and last
      revealedWords = [ladder[0].word, ladder[ladder.length - 1].word];
    } catch (error) {
      console.error('Error loading puzzle:', error);
    }
  });

function handleInput(event) {
  if (event.key === 'Enter') {
    const word = currentInput.toUpperCase();
    
    // Find next empty position from top and bottom
    const topIndex = ladder.findIndex(rung => !rung.isRevealed);
    const bottomIndex = ladder.length - 1 - [...ladder].reverse().findIndex(rung => !rung.isRevealed);
    
    // Check if word matches either position
    if (isValidWord(word, topIndex) || isValidWord(word, bottomIndex)) {
      const matchIndex = isValidWord(word, topIndex) ? topIndex : bottomIndex;
      ladder[matchIndex].isRevealed = true;
      revealedWords = [...revealedWords, word];
      
      // Mark clue as used - look at transformation after the word for bottom-up matches
      const clueIndex = clues.findIndex(clue => {
        if (matchIndex === topIndex) {
          // For top-down matches, use previous transformation
          return clue.text === ladder[matchIndex - 1].transformation;
        } else {
          // For bottom-up matches, use next transformation
          return clue.text === ladder[matchIndex].transformation;
        }
      });
      
      if (clueIndex !== -1) {
        clues[clueIndex].isUsed = true;
      }
      
      currentInput = '';
      errorMessage = '';
      
      // Check if game is complete
      gameComplete = ladder.every(rung => rung.isRevealed);
      
      // If game is complete, mark any remaining clues as used
      if (gameComplete) {
        clues = clues.map(clue => ({...clue, isUsed: true}));
      }
    } else {
      errorMessage = 'That word doesn\'t fit here!';
    }
  }
}

  function isValidWord(word, index) {
    return ladder[index]?.word === word;
  }
</script>

<main class="min-h-screen bg-gray-100 p-4">
  <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
    <!-- Left side: Ladder -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold mb-6">RADDLE — Transformation Ladder</h2>
      <div class="space-y-4">
        {#each ladder as rung, index}
          <div class="flex items-center space-x-4">
            <div class="w-12 text-center text-gray-500">
              {index + 1}.
            </div>
            <div class="flex-1 p-3 rounded {rung.isRevealed ? 
              'bg-green-100 border' : 
              ((!rung.isRevealed && 
                (index === ladder.findIndex(r => !r.isRevealed) || 
                 index === ladder.length - 1 - [...ladder].reverse().findIndex(r => !r.isRevealed))
              ) ? 'bg-blue-50 border-blue-300 border-2' : 'bg-gray-50')}">
              {#if rung.isRevealed}
                <span class="font-mono text-lg">{rung.word}</span>
              {:else}
                <span class="text-gray-400">{rung.word.length} letters</span>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Right side: Clues and Input -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold mb-6">Transformations, in alpha order</h2>
      <div class="space-y-4 mb-8">
        {#each clues as clue}
          <div class="p-3 border rounded {clue.isUsed ? 'line-through text-gray-400' : ''}">
            {clue.text}
          </div>
        {/each}
      </div>

      {#if !gameComplete}
        <div class="mt-6">
          <input
            type="text"
            bind:value={currentInput}
            on:keydown={handleInput}
            placeholder="Submit word for either of the next rungs"
            class="w-full p-3 border-2 border-blue-300 rounded bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {#if errorMessage}
            <p class="text-red-500 mt-2">{errorMessage}</p>
          {/if}
        </div>
      {:else}
        <div class="text-center p-4 bg-green-100 rounded">
          <h3 class="text-xl font-bold text-green-700">Congratulations!</h3>
          <p>You've completed the word ladder!</p>
        </div>
      {/if}
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }
</style>