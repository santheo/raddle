<script>
  import { onMount } from 'svelte';
  import { load } from 'js-yaml';

  let ladder = $state([]);
  let clues = $state([]);
  let emoji1 = $state([]);
  let emoji2 = $state([]);
  let revealedWords = $state([]);
  let currentInput = $state('');
  let gameComplete = $state(false);
  let errorMessage = $state('');
  let inputElement; // store the input element reference
  
  onMount(async () => {
    try {
      const response = await fetch('/data/caterpillar-butterfly.yaml');
      const text = await response.text();
      const data = load(text);

      emoji1 = data.meta.emoji1;
      emoji2 = data.meta.emoji2;
      
      // Process the ladder data from YAML
      ladder = data.ladder.map((node, index) => ({
        word: node.word,
        clue: node.clue,
        transform: index > 0 ? data.ladder[index - 1].transform : "",  // Get transform from previous node
        isRevealed: index === 0 || index === data.ladder.length - 1,
        isClueShown: false,
        isNext: false
      }));
      
      // Create alphabetically sorted clues
      clues = data.ladder
        .filter(node => node.clue)
        .map(node => ({
          text: node.clue,
          isUsed: false
        }))
        .sort((a, b) => a.text.localeCompare(b.text));
      
      // Initialize revealed words with first and last
      revealedWords = [ladder[0].word, ladder[ladder.length - 1].word];
      
      // Focus the input element
      inputElement?.focus();
      updateNextRungs(); 
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
      updateNextRungs(); // Add this line
      revealedWords = [...revealedWords, word];
      
      // Show clues based on direction
      if (matchIndex === topIndex) {
        // Going down from top - show clues for all previous rungs
        ladder = ladder.map((rung, i) => ({
          ...rung,
          isClueShown: rung.isClueShown || i <= matchIndex
        }));
      } else {
        // Going up from bottom - show clues for all following rungs
        ladder = ladder.map((rung, i) => ({
          ...rung,
          isClueShown: rung.isClueShown || i > matchIndex
        }));
      }

      // Mark clue as used - look at transformation after the word for bottom-up matches
      const clueIndex = clues.findIndex(clue => {
        if (matchIndex === topIndex) {
          // For top-down matches, use previous transformation
          return clue.text === ladder[matchIndex - 1].clue;
        } else {
          // For bottom-up matches, use next transformation
          return clue.text === ladder[matchIndex].clue;
        }
      });
      
      if (clueIndex !== -1) {
        clues[clueIndex].isUsed = true;
      }
      
      currentInput = '';
      errorMessage = '';
      
      // Check if game is complete
      gameComplete = ladder.every(rung => rung.isRevealed);
      
      // If game is complete, mark all clues as used and show all clue transformations
      if (gameComplete) {
        ladder = ladder.map(rung => ({...rung, isClueShown: true}));
        clues = clues.map(clue => ({...clue, isUsed: true}));
      }
    } else {
      errorMessage = `${word} is not correct.`;
      currentInput = '';
      inputElement?.focus();
    }
  }
}

  function isValidWord(word, index) {
    return ladder[index]?.word === word;
  }

  function updateNextRungs() {
    const topNextIndex = ladder.findIndex(r => !r.isRevealed);
    const bottomNextIndex = ladder.length - 1 - [...ladder].reverse().findIndex(r => !r.isRevealed);
    
    ladder = ladder.map((rung, index) => ({
      ...rung,
      isNext: !rung.isRevealed && (index === topNextIndex || index === bottomNextIndex)
    }));
  }
</script>

<main class="min-h-screen bg-gray-100 p-4">
  <div class="max-w-6xl mx-auto">
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-bold ">RADDLE — The Transformation Ladder Game</h2>
      <p>This is a demo version. It only works on desktop browsers for now. <b>Please don't share.</b> Direct all feedback to <a class="text-blue-600 underline" href="mailto:sandy@mysteryleague.com">sandy@mysteryleague.com</a>.</p>
    </div>  
    <!-- Top section: Input -->
    {#if !gameComplete}
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="max-w-2xl mx-auto">
        <p class="mb-2">
          Guess the word that goes in either of the active rungs:
        </p>
        <input
          bind:this={inputElement}
          type="text"
          bind:value={currentInput}
          onkeydown={handleInput}
          placeholder="Type a word here…"
          class="w-full p-3 border-2 border-blue-300 rounded bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {#if errorMessage}
          <p class="text-red-500 mt-2">{errorMessage}</p>
        {/if}
      </div>
    </div>
    {:else}
      <div class="text-center p-4 bg-green-100 rounded mb-4">
        <h3 class="text-xl font-bold text-green-700">Congratulations!</h3>
        <p>You've successfully climbed the ladder!</p>
      </div>
    {/if}

    <!-- Main grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

      <!-- Clues -->
      <div class="md:order-2 bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold mb-2">Transformations</h2>
        <p class="mb-4 text-sm">To find the next word in the ladder, answer one of the questions below. 
          It's up to you to determine which one.
          You may also work from the bottom of the ladder, going up.
        </p>
        <div class="space-y-3">
          {#each clues as clue}
            <div class="p-3 rounded bg-gray-100 {clue.isUsed ? 'line-through text-gray-400' : ''}">
              {@html clue.text.replace('^', `<span class="word-placeholder">&nbsp;</span>`)}
            </div>
          {/each}
        </div>

      </div>

      <!-- Ladder -->
      <div>
      <div class="bg-white rounded-lg shadow">
        <div class="divide-y divide-gray-300">
          {#each ladder as rung, index}
          
          <div class="p-4 relative font-mono text-lg" class:bg-blue-50={rung.isNext} class:bg-green-100={rung.isRevealed}>
              {#if rung.isRevealed}
                {#if rung.isClueShown}
                  <span class="font-serif transform">{rung.transform}</span>
                {/if}
                {#if ladder[index + 1]?.isNext}
                  <!-- {emoji1} -->
                {/if}
                {rung.word}
                {#if ladder[index + 1]?.isNext}
                  <!-- {emoji1} -->
                {/if}
              {:else}
                <span class="">
                  {#each rung.word.split(' ') as word, i}
                    <span class="word-box">
                    {#each Array(word.length) as _, j}
                      <span class="letter-box">&nbsp;</span>
                    {/each}
                    </span>
                  {/each}
                  <span class="ml-1">
                    ({rung.word.split(' ').map(w => w.length).join(' ')})
                  </span>
                </span>
              {/if}
            </div>
          {/each}
        </div>
      </div>
        {#if process.env.NODE_ENV === 'development'}
        <div class="mt-4">
          <button
            onclick={() => {
              ladder = ladder.map(rung => ({
                ...rung,
                isRevealed: true,
                isClueShown: true,
                isNext: false
              }));
              
              setTimeout(() => {
                clues = clues.map(clue => ({
                  ...clue,
                  isUsed: true
                }));
                gameComplete = true;
              }, 0);
              gameComplete = true;
            }}
            class="w-full p-2 mt-4 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded"
          >
            [DEBUG] Reveal Ladder
          </button>
        </div>
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }

  :global(.revealed) {
    border: 1px solid rgb(74, 222, 128); /* matches border color of revealed words */
  }

  :global(.word-placeholder) {
    display: inline-block;
    background-color: rgb(220, 252, 231); /* matches bg-green-100 */
    border: 1px solid rgb(74, 222, 128); /* matches border color of revealed words */
    border-radius: 0.25rem;
    padding: 0 0.5rem;
    margin-right: 1px;
  }

  :global(.word-box:not(:first-child)) {
    display: inline-block;
    margin-left: 10px;
  }

  :global(.letter-box) {
    display: inline-block;
    width: 1em;
    height: 1em;
    background: #ccc;
    margin: 0 3px 0 0;
    text-align: center;
    line-height: 1em;
  }
  
  :global(.transform) {
    font-size: .9rem;
    font-style: italic;
    background-color: rgb(220, 252, 231);
    position: absolute;
    top: -.8rem;
    left: calc(var(--spacing)*2);
    padding: 0 .5rem;
    opacity: .7;
  }
</style>