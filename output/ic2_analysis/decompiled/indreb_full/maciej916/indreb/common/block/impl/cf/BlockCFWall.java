package com.maciej916.indreb.common.block.impl.cf;

import com.maciej916.indreb.common.item.impl.Painter;
import com.maciej916.indreb.common.registries.ModSounds;
import com.maciej916.indreb.common.util.GuiUtil;
import com.mojang.math.Vector3f;
import java.util.Random;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;
import net.minecraft.world.level.material.MaterialColor.Brightness;
import net.minecraft.world.phys.BlockHitResult;

public class BlockCFWall extends Block {
   public BlockCFWall(MaterialColor color) {
      super(Properties.m_60944_(Material.f_76278_, color).m_60913_(5.0F, 60.0F).m_60918_(SoundType.f_56742_));
   }

   public InteractionResult m_6227_(
      BlockState blockState, Level level, BlockPos blockPos, Player player, InteractionHand interactionHand, BlockHitResult blockHitResult
   ) {
      if (!(player.m_21120_(interactionHand).m_41720_() instanceof Painter painter)) {
         return super.m_6227_(blockState, level, blockPos, player, interactionHand, blockHitResult);
      } else if (painter.getState() == blockState) {
         return InteractionResult.PASS;
      } else {
         BlockPos dropPos = blockPos.m_142300_(blockHitResult.m_82434_());
         Random random = new Random();
         Direction dir = blockHitResult.m_82434_();
         int rgbColor = painter.getColor().m_192921_(Brightness.NORMAL);
         Vector3f COLOR = new Vector3f(GuiUtil.getBlue(rgbColor), GuiUtil.getGreen(rgbColor), GuiUtil.getRed(rgbColor));

         for (int i = 0; i < 5; i++) {
            double x;
            double y;
            double z;
            if (dir != Direction.UP && dir != Direction.DOWN) {
               y = (double)dropPos.m_123342_() + Math.random() * 0.6000000000000001 + 0.2;
               if (dir != Direction.WEST && dir != Direction.EAST) {
                  x = (double)dropPos.m_123341_() + Math.random() * 0.6000000000000001 + 0.2;
                  z = (double)dropPos.m_123343_() + (dir == Direction.SOUTH ? Math.random() * 0.2 + 0.0 : Math.random() * 0.19999999999999996 + 0.8);
               } else {
                  x = (double)dropPos.m_123341_() + (dir == Direction.EAST ? Math.random() * 0.2 + 0.0 : Math.random() * 0.19999999999999996 + 0.8);
                  z = (double)dropPos.m_123343_() + Math.random() * 0.6000000000000001 + 0.2;
               }
            } else {
               x = (double)dropPos.m_123341_() + Math.random() * 0.6000000000000001 + 0.2;
               y = (double)dropPos.m_123342_() + (dir == Direction.UP ? Math.random() * 0.2 + 0.0 : Math.random() * 0.19999999999999996 + 0.8);
               z = (double)dropPos.m_123343_() + Math.random() * 0.6000000000000001 + 0.2;
            }

            level.m_7106_(new DustParticleOptions(COLOR, 1.0F), x, y, z, 0.0, 0.0, 0.0);
         }

         if (!level.m_5776_()) {
            level.m_6263_(
               null,
               (double)blockPos.m_123341_(),
               (double)blockPos.m_123342_(),
               (double)blockPos.m_123343_(),
               ModSounds.PAINTER,
               SoundSource.PLAYERS,
               1.0F,
               1.0F
            );
            level.m_7731_(blockPos, painter.getState(), 2);
            player.m_21120_(interactionHand)
               .m_41622_(
                  1,
                  player,
                  ix -> level.m_6263_(
                        null,
                        player.m_20185_(),
                        player.m_20186_(),
                        player.m_20189_(),
                        SoundEvents.f_12018_,
                        SoundSource.BLOCKS,
                        0.5F,
                        0.4F / (random.nextFloat() * 0.4F + 0.8F)
                     )
               );
         }

         return InteractionResult.SUCCESS;
      }
   }
}
